import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom'; // Import useNavigate and useLocation

const Results = () => {
    const [userChoices, setUserChoices] = useState([]);
    const navigate = useNavigate(); // Initialize navigate function
    const location = useLocation(); // Initialize useLocation hook

    useEffect(() => {
        if (location.state && location.state.userChoices) {
            setUserChoices(location.state.userChoices);
        } else {
            console.error("No user choices found in location state");
        }    
    }, [location.state]);

    return (
        <div>
            <h1>Results</h1>
            <button onClick={() => navigate("/")}>Run another experiment</button>

            <h2>Total Results</h2>
            <p>Preference of Human text: {userChoices.filter(choice => choice.choice === 'human').length}</p>
            <p>Preference of LLM text: {userChoices.filter(choice => choice.choice === 'llm').length}</p>
            <p>No Preference: {userChoices.filter(choice => choice.choice === 'none').length}</p>
            
            <h2>Individual Choices</h2>
            {userChoices.map((choice, index) => (
                <div key={index}>
                    <h3>Choice {choice.index}</h3>
                    <p>Chosen Option: {choice.choice}</p>
                    <p>Title: {choice.description.human.title}</p>
                </div>
            ))}
        </div>
    );
};

export default Results;
