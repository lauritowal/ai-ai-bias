import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate

const Results = () => {
    const [userChoices, setUserChoices] = useState([]);
    const navigate = useNavigate(); // Initialize navigate function

    useEffect(() => {
        const storedChoices = localStorage.getItem('userChoices');
        if (storedChoices) {
            setUserChoices(JSON.parse(storedChoices));
        }
        console.log("storedChoices", storedChoices)
    }, []);

    return (
        <div>
            <h1>Results</h1>
            {userChoices.map((choice, index) => (
                <div key={index}>
                    <h2>Choice {index + 1}</h2>
                    <p>Chosen Option: {choice.choice}</p>
                    <p>Description Index: {choice.index}</p>
                </div>
            ))}
            <button onClick={() => navigate("/")}>Run another experiment</button>
        </div>
    );
};

export default Results;
