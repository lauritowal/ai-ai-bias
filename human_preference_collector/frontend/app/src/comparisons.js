import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom'; // Import useNavigate
import axios from 'axios'; 

const Comparisons = () => {
    const [descriptions, setDescriptions] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [currentDescription, setCurrentDescription] = useState(null);
    const [isHumanFirst, setIsHumanFirst] = useState(Math.random() > 0.5);
    const [userChoices, setUserChoices] = useState([]);
    const navigate = useNavigate(); // Initialize navigate function
    const location = useLocation(); // Initialize useLocation hook

    useEffect(() => {
        if (location.state && location.state.descriptions) {
            const descriptions = location.state.descriptions;
            setDescriptions(descriptions);
            setCurrentDescription(descriptions[0]);
            
            if (descriptions.length > 0 && currentIndex < descriptions.length) {
                setCurrentDescription(descriptions[currentIndex]);
                setIsHumanFirst(Math.random() > 0.5);
            } else if (currentIndex >= descriptions.length) {
                const submit = async () => {
                    try {
                        const response = await axios.post('http://localhost:5000/submit', {
                            username: JSON.parse(localStorage.getItem('user')).name,
                            email: JSON.parse(localStorage.getItem('user')).email,
                            category: localStorage.getItem('category'),
                            model: localStorage.getItem('model'),
                            userChoices: userChoices,
                            totalLLMChoices: userChoices.filter(choice => choice.choice === 'llm').length,
                            totalHumanChoices: userChoices.filter(choice => choice.choice === 'human').length,
                            totalNoPreference: userChoices.filter(choice => choice.choice === 'none').length
                        });
                        console.log(response.data);
                        navigate('/results', { state: { userChoices: userChoices } });
                    } catch (error) {
                        console.error('Error submitting form:', error);
                    }
                };
                submit();
            }
        }
    }, [currentIndex, navigate, userChoices]);

    const handleUserChoice = (choice) => {
        setUserChoices(prevChoices => [...prevChoices, {
            index: currentIndex,
            choice: choice,
            description: currentDescription
        }]);
        setCurrentIndex(currentIndex + 1);
    };

    return (
        <div>
            {currentDescription ? (
                <div>
                    <h1>Comparison</h1>
                    <h3>{currentIndex + 1} / {descriptions.length}</h3>
                    <div>
                        <button onClick={() => handleUserChoice(isHumanFirst ? 'human' : 'llm')}>Prefer Option A</button>
                        <button onClick={() => handleUserChoice(isHumanFirst ? 'llm' : 'human')}>Prefer Option B</button>
                        <button onClick={() => handleUserChoice('none')}>No Preference</button>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
                        <div>
                            <h2>Text Option A</h2>
                            <p>{isHumanFirst ? (currentDescription.human.descriptions ? currentDescription.human.descriptions[0] : currentDescription.human.abstract) : JSON.stringify(currentDescription.llm.descriptions[0])}</p>
                        </div>
                        <div>
                            <h2>Text Option B</h2>
                            <p>{isHumanFirst ? JSON.stringify(currentDescription.llm.descriptions[0]) : (currentDescription.human.descriptions ? currentDescription.human.descriptions[0] : currentDescription.human.abstract)}</p>
                        </div>
                    </div>
                </div>
            ) : (
                <p>Loading descriptions...</p>
            )}
        </div>
    );
};

export default Comparisons;
