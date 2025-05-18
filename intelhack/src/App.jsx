import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import UploadPage from "./UploadPage";
import QuestionPage from "./QuestionPage";
import FinishPage from "./FinishPage";
// import About from "./About";
function App() {
return (
<div>
<BrowserRouter>
<Routes>
    <Route path="/" element={<UploadPage />} />
    <Route path="/upload" element={<UploadPage />} />
    <Route path="/questions" element={<QuestionPage />}/>
    <Route path="/end" element={<FinishPage />}/>
    {/* <Route path="/about" element={<About />}></Route> */}
</Routes>
</BrowserRouter>
</div>
);
}
export default App;