import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate

const Comparisons = () => {
    const [descriptions, setDescriptions] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [currentDescription, setCurrentDescription] = useState(null);
    const [isHumanFirst, setIsHumanFirst] = useState(Math.random() > 0.5);
    const [userChoices, setUserChoices] = useState([]);
    const navigate = useNavigate(); // Initialize navigate function

    useEffect(() => {
        const storedDescriptions = localStorage.getItem('descriptions');
        if (storedDescriptions) {
            const loadedDescriptions = JSON.parse(storedDescriptions);
            setDescriptions(loadedDescriptions);
            setCurrentDescription(loadedDescriptions[0]);
            
            if (loadedDescriptions.length > 0 && currentIndex < loadedDescriptions.length) {
                setCurrentDescription(loadedDescriptions[currentIndex]);
                setIsHumanFirst(Math.random() > 0.5);
            } else if (currentIndex >= descriptions.length) {
                localStorage.setItem('userChoices', JSON.stringify(userChoices)); // Store choices for later use
                navigate('/results'); 
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
                    <div>
                        <button onClick={() => handleUserChoice(isHumanFirst ? 'human' : 'llm')}>Prefer Option A</button>
                        <button onClick={() => handleUserChoice(isHumanFirst ? 'llm' : 'human')}>Prefer Option B</button>
                        <button onClick={() => handleUserChoice('none')}>No Preference</button>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
                        <div>
                            <h2>Text Option A</h2>
                            <p>{isHumanFirst ? (currentDescription.human.description || currentDescription.human.abstract) : currentDescription.llm.descriptions[0]}</p>
                        </div>
                        <div>
                            <h2>Text Option B</h2>
                            <p>{isHumanFirst ? currentDescription.llm.descriptions[0] : (currentDescription.human.description || currentDescription.human.abstract)}</p>
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
