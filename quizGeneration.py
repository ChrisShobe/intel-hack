import re
import json
from transformers import pipeline, T5ForConditionalGeneration, T5Tokenizer

class EnhancedQuizSystem:
    def __init__(self, use_refinement=True):
        # Initialize components
        self.generator = QuizGenerator()
        self.quality_filter = QuestionQualityFilter()
        self.use_refinement = use_refinement
        self.refinement_model = self.load_refinement_model() if use_refinement else None
        
    def load_refinement_model(self):
        """Load the trained T5 model for question refinement"""
        try:
            model = T5ForConditionalGeneration.from_pretrained("models/slide2quiz-model")
            tokenizer = T5Tokenizer.from_pretrained("models/slide2quiz-model")
            return pipeline(
                "text2text-generation", 
                model=model, 
                tokenizer=tokenizer,
                device=-1  # Use CPU to save memory
            )
        except Exception as e:
            print(f"Warning: Could not load refinement model ({str(e)}), using basic filtering only")
            return None
    
    def clean_text(self, text):
        """Clean unwanted characters and formatting"""
        if not isinstance(text, str):
            return ""
            
        text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)  # Remove unicode escapes
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
        text = re.sub(r'[“”„‟]', '"', text)  # Normalize quotes
        text = re.sub(r'[‘’‛`]', "'", text)  # Normalize apostrophes
        return text
    
    def refine_question(self, question, context):
        """Use ML model to improve poorly phrased questions"""
        if not self.refinement_model:
            return question
            
        try:
            prompt = f"improve this question: {question} using context: {context[:300]}"
            refined = self.refinement_model(
                prompt, 
                max_length=100,
                num_beams=3,
                early_stopping=True
            )[0]['generated_text']
            
            # Ensure the refined question ends with a question mark
            refined = refined.strip()
            if not refined.endswith('?'):
                refined += '?'
            return refined
        except Exception as e:
            print(f"Question refinement failed: {str(e)}")
            return question
    
    def refine_answer(self, answer, question):
        """Clean and improve answers based on the question"""
        answer = self.clean_text(answer)
        
        # Remove citations and references
        answer = re.sub(r'\([^)]*\)', '', answer)  # Remove parentheses content
        answer = re.sub(r'\[[^\]]*\]', '', answer)  # Remove bracket content
        
        # Remove unnecessary clauses
        answer = re.sub(r'(?:Note|Important|Recall that|See also)[^.!?]*[.!?]', '', answer)
        
        # Focus the answer on the question's subject
        if "define" in question.lower() or "what is" in question.lower():
            # For definition questions, take just the first complete definition
            sentences = re.split(r'(?<=[.!?])\s+', answer)
            if sentences:
                return sentences[0]
        
        # For other questions, limit to 2 sentences
        sentences = re.split(r'(?<=[.!?])\s+', answer)
        if len(sentences) > 2:
            answer = ' '.join(sentences[:2])
        
        return answer
    
    def is_question_valid(self, question_item, context):
        """Comprehensive validation of question-answer pairs"""
        question = question_item['question']
        answer = question_item['answer']
        term = question_item.get('term', '')
        
        # Check for trivial terms
        trivial_terms = {'it', 'they', 'them', 'this', 'that', 'there', 
                        'have', 'has', 'had', 'do', 'does', 'did'}
        if term.lower() in trivial_terms:
            return False
            
        # Check question structure
        if (not question.endswith('?') or 
            len(question.split()) < 4 or 
            len(question) < 10):
            return False
            
        # Check answer quality
        if (answer.lower() == "definition not found in the text" or
            len(answer.split()) < 3 or
            len(answer) < 10):
            return False
            
        # Check if answer actually addresses the question
        if term and term.lower() not in answer.lower():
            return False
            
        return True
    
    def process_text(self, full_text, min_quality=0.7):
        """Full processing pipeline with quality control"""
        # Generate initial questions
        quiz_data = self.generator.process_text(full_text)
        final_output = []
        
        for chunk in quiz_data:
            if not chunk.get('questions'):
                continue
                
            text_chunk = chunk['text_preview']
            filtered_questions = []
            
            for question_item in chunk['questions']:
                # Initial cleaning
                question_item['question'] = self.clean_text(question_item['question'])
                question_item['answer'] = self.clean_text(question_item['answer'])
                
                # Skip invalid questions early
                if not self.is_question_valid(question_item, text_chunk):
                    continue
                
                # Refine answer based on question
                question_item['answer'] = self.refine_answer(
                    question_item['answer'],
                    question_item['question']
                )
                
                # Quality assessment
                quality_score = self.quality_filter.score_question(
                    question_item['question'],
                    text_chunk
                )
                
                # Try to improve low-quality questions
                if quality_score < min_quality and self.use_refinement:
                    refined_question = self.refine_question(
                        question_item['question'],
                        text_chunk
                    )
                    refined_score = self.quality_filter.score_question(
                        refined_question,
                        text_chunk
                    )
                    
                    if refined_score >= quality_score:  # Only keep if improved
                        question_item['question'] = refined_question
                        quality_score = refined_score
                
                # Final quality check
                if quality_score >= min_quality:
                    question_item['confidence'] = round(quality_score, 2)
                    filtered_questions.append(question_item)
            
            # Keep best questions per chunk
            if filtered_questions:
                filtered_questions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
                final_output.append({
                    'chunk_number': chunk['chunk_number'],
                    'text_preview': chunk['text_preview'],
                    'questions': filtered_questions[:5]  # Top 5 questions
                })
        
        return final_output

class QuestionQualityFilter:
    def __init__(self):
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # Use CPU
            )
            self.labels = [
                "clear academic question",
                "grammatically correct",
                "answerable from given text",
                "conceptually sound",
                "focused on key concepts"
            ]
        except Exception as e:
            print(f"Could not initialize quality filter: {str(e)}")
            self.classifier = None
    
    def score_question(self, question, context):
        if not self.classifier:
            return 0.7  # Default passing score if filter unavailable
            
        try:
            result = self.classifier(
                question,
                self.labels,
                multi_label=True,
                hypothesis_template="This question is about {}."
            )
            # Weight the scores (focus more on clarity and answerability)
            weights = [0.4, 0.2, 0.3, 0.05, 0.05]
            weighted_score = sum(s*w for s,w in zip(result['scores'], weights))
            return min(1.0, weighted_score * 1.2)  # Slight boost
        except:
            return 0.5  # Neutral score if classification fails

# Your QuizGenerator class would remain the same as before