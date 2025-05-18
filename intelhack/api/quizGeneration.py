import re
import csv
import json
from typing import List, Dict


class RobustQuizGenerator:
    def __init__(self):
        # Simplified and escaped regex patterns
        self.definition_patterns = [
            r"\b{term}\b (?:is|are|refers to|means|is defined as|is called|is known as|denotes|represents)",
            r"\b(The|A|An)\b {term}\b (?:is|are|was|were)",
            r"\b{term}\b(?:, which| that) (?:is|are|has|have|can|may)",
            r"\b(?:Function|Purpose|Role|Concept)\b of {term}\b (?:is|are)",
            r"\b{term}\b (?:plays|serves|acts as) (?:a|an|the) (?:key|important|crucial) (?:role|part|function)",
            r"\b{term}\b (?:is|are) (?:used for|employed in|important for|critical to)",
            r"\bIn\b (?:.*?), {term}\b (?:is|are)"
        ]
       
        self.question_templates = [
            "What is {term}?",
            "Define {term}.",
            "What is the purpose of {term}?",
            "Explain {term}.",
            "Describe {term}.",
            "What does {term} mean?",
            "How would you explain {term}?",
            "What is the significance of {term}?"
        ]
       
        self.excluded_terms = {
            'page', 'chunk', 'it', 'these', 'this', 'that', 'they', 'their',
            'there', 'which', 'what', 'where', 'when', 'how', 'why', 'kugonza',
            'arthur', 'note', 'drawing', 'example', 'examples', 'has', 'have',
            'had', 'having', 'use', 'used', 'using', 'each', 'some', 'many',
            'and', 'the', 'are', 'for', 'with', 'from'
        }


    def clean_text(self, text: str) -> str:
        """Remove unwanted patterns and clean the text"""
        if not text:
            return ""
           
        try:
            text = re.sub(r'--- Page \d+ ---', '', text)
            text = re.sub(r'@Kugonza Arthur H 0701 366474', '', text)
            text = re.sub(r'S\.1 BIOLOGY TEACHING NOTES', '', text)
            text = re.sub(r'--- Chunk \d+ ---', '', text)
            return ' '.join(text.split())
        except Exception as e:
            print(f"Error cleaning text: {str(e)}")
            return text


    def safe_regex_search(self, pattern: str, text: str) -> bool:
        """Safely check if a regex pattern matches text"""
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error:
            return False


    def extract_meaningful_terms(self, text: str) -> List[str]:
        """Extract potential terms for questions with robust patterns"""
        if not text:
            return []
           
        # Simple and safe patterns
        patterns = [
            r'\b([A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]+)*\b)',  # Capitalized terms
            r'\b([a-z]{3,}\s+(?:theory|concept|method|principle|law|model|cell|tissue|organ|system))\b',
            r'\b([A-Za-z]{3,}\s+[A-Za-z]{3,})\b(?=\s+is|\s+are|\s+means)',  # Terms before definitions
        ]
       
        candidates = []
        for pattern in patterns:
            try:
                matches = re.findall(pattern, text)
                candidates.extend(matches)
            except re.error as e:
                print(f"Regex error with pattern '{pattern}': {str(e)}")
                continue
       
        # Filter terms
        filtered = []
        for term in candidates:
            term_lower = term.lower()
            if (term_lower not in self.excluded_terms and
                len(term.split()) <= 3 and
                len(term) >= 4 and
                not term.isnumeric()):
                filtered.append(term)
       
        # Count occurrences
        term_counts = {}
        for term in filtered:
            term_counts[term] = term_counts.get(term, 0) + text.lower().count(term.lower())
       
        return sorted(term_counts.keys(), key=lambda x: term_counts[x], reverse=True)[:5]


    def find_definition(self, text: str, term: str) -> str:
        """Find a definition or explanation for the given term"""
        if not text or not term:
            return ""
           
        sentences = re.split(r'(?<=[.!?])\s+', text)
        term_lower = term.lower()
       
        for sent in sentences:
            if term_lower in sent.lower():
                # Try each definition pattern safely
                for pat in self.definition_patterns:
                    try:
                        regex = pat.format(term=re.escape(term))
                        if re.search(regex, sent, re.IGNORECASE):
                            return self.clean_text(sent)
                    except re.error as e:
                        print(f"Regex error in definition pattern: {str(e)}")
                        continue
               
                # Fallback: return the sentence if it contains the term
                return self.clean_text(sent)
       
        return ""


    def generate_questions(self, text: str) -> List[Dict[str, str]]:
        """Generate quiz questions with robust error handling"""
        if not text:
            return []
           
        cleaned_text = self.clean_text(text)
        terms = self.extract_meaningful_terms(cleaned_text)
        questions = []
       
        for i, term in enumerate(terms):
            try:
                answer = self.find_definition(cleaned_text, term)
               
                # Skip if answer is poor quality
                if not answer or len(answer.split()) < 5:
                    continue
                   
                # Skip if answer just repeats the term
                term_words = set(term.lower().split())
                answer_words = set(answer.lower().split())
                if term_words.issubset(answer_words):
                    continue
                   
                question = self.question_templates[i % len(self.question_templates)].format(term=term)
                questions.append({
                    "question": question,
                    "answer": answer,
                    "term": term
                })
                if len(questions) >= 3:
                    break
            except Exception as e:
                print(f"Error generating question for term '{term}': {str(e)}")
                continue
               
        return questions


    def process_text(self, full_text: str) -> List[Dict[str, any]]:
        """Process the full text with error handling"""
        if not full_text:
            return []
           
        try:
            chunks = re.split(r'\n{2,}|(?=\b(?:Section|Chapter|Unit|TOPIC)\b)', full_text)
            results = []
           
            for idx, chunk in enumerate(chunks):
                try:
                    chunk = self.clean_text(chunk.strip())
                    if not chunk or len(chunk) < 100:
                        continue
                       
                    questions = self.generate_questions(chunk)
                    if questions:
                        results.append({
                            "chunk_number": idx + 1,
                            "text_preview": chunk[:200] + ("..." if len(chunk) > 200 else ""),
                            "questions": questions
                        })
                except Exception as e:
                    print(f"Error processing chunk {idx + 1}: {str(e)}")
                    continue
                   
            return results
        except Exception as e:
            print(f"Error splitting text into chunks: {str(e)}")
            return []


def save_output(data: List[Dict[str, any]], filename: str, format: str = 'json'):
    """Save output in specified format with error handling"""
    if not data:
        print("No data to save")
        return
       
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(data, f, ensure_ascii=False, indent=2)
            elif format == 'csv':
                writer = csv.writer(f)
                writer.writerow(['Chunk Number', 'Text Preview', 'Question', 'Answer', 'Term'])
                for chunk in data:
                    for question in chunk['questions']:
                        writer.writerow([
                            chunk['chunk_number'],
                            chunk['text_preview'],
                            question['question'],
                            question['answer'],
                            question.get('term', '')
                        ])
        print(f"Successfully saved {len(data)} records to {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {str(e)}")


def main():
    input_filename = "chunk.txt"
    output_json = "quiz_data.json"
    output_csv = "quiz_output.csv"
   
    try:
        print(f"Reading input file: {input_filename}")
        with open(input_filename, 'r', encoding='utf-8') as f:
            full_text = f.read()
           
        if not full_text.strip():
            print("Error: Input file is empty")
            return
           
        print("Processing text...")
        generator = RobustQuizGenerator()
        quiz_data = generator.process_text(full_text)
       
        if quiz_data:
            print(f"Generated {sum(len(chunk['questions']) for chunk in quiz_data)} questions")
            save_output(quiz_data, output_json, 'json')
            save_output(quiz_data, output_csv, 'csv')
        else:
            print("No quiz questions were generated. Possible reasons:")
            print("- The text doesn't contain clear definitions or explanations")
            print("- The terms found were filtered out as too common")
            print("- The text structure may need different parsing")
            print("Try adjusting the excluded_terms or definition_patterns in the code.")
           
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def generate_quiz_from_chunk_file(input_path: str, json_out: str, csv_out: str):
    try:
        print(f"[✓] Reading chunked input from: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        if not full_text.strip():
            print("[!] Input file is empty")
            return []

        generator = RobustQuizGenerator()
        quiz_data = generator.process_text(full_text)

        if quiz_data:
            print(f"[✓] Generated {sum(len(chunk['questions']) for chunk in quiz_data)} questions")
            save_output(quiz_data, json_out, 'json')
            save_output(quiz_data, csv_out, 'csv')
        else:
            print("[!] No quiz questions generated.")
        
        return quiz_data

    except FileNotFoundError:
        print(f"[!] Input file '{input_path}' not found.")
        return []
    except Exception as e:
        print(f"[!] Unexpected error: {str(e)}")
        return []