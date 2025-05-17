import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./UploadPage";
import UploadPage from "./UploadPage";
// import About from "./About";
function App() {
return (
<div>
<BrowserRouter>
<Routes>
    <Route path="/" element={<UploadPage />}></Route>
    <Route path="/upload" element={<UploadPage />} />
    {/* <Route path="/about" element={<About />}></Route> */}
</Routes>
</BrowserRouter>
</div>
);
}
export default App;