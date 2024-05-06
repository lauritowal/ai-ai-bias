import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Setup = () => {
    const categories = ["paper", "product"];
    const models = ["gpt3_5", "gpt4"];
    const [selectedCategory, setSelectedCategory] = useState(categories[0]);
    const [selectedModel, setSelectedModel] = useState(models[0]);
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        const storedUser = localStorage.getItem("user");
        if (storedUser) {
            const user = JSON.parse(storedUser);
            setUsername(user.name);
            setEmail(user.email);
        }
    }, []); // Run once after component mount

    const handleUsernameChange = (event) => {
        setUsername(event.target.value);
    };

    const handleEmailChange = (event) => {
        setEmail(event.target.value);
    };

    const handleCategoryChange = (event) => {
        setSelectedCategory(event.target.value);
    };

    const handleModelChange = (event) => {
        setSelectedModel(event.target.value);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!username.trim()) {
            setError('Username cannot be empty');
            return;
        }

        localStorage.clear();

        try {
            const response = await axios.post('http://localhost:5000/descriptions', {
                username: username,
                email: email,
                category: selectedCategory,
                model: selectedModel
            });
            if (response.data && response.data.length > 0) {
                localStorage.setItem('user', JSON.stringify({ name: username, email: email }));
                localStorage.setItem('model', selectedModel);
                localStorage.setItem('category', selectedCategory);
                navigate('/comparisons', { state: { descriptions: response.data } });
            } else {
                console.error('No data received from the server');
                // Handle error
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            // Handle error
        }
    };

    return (
        <div>
            <h1>Setup Configuration</h1>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>
                        Username:
                        <input type="text" name="username" value={username} onChange={handleUsernameChange} />
                    </label>
                </div>
                <div>
                    <label>
                        Email:
                        <input type="email" name="email" value={email} onChange={handleEmailChange} />
                    </label>
                </div>
                <div>
                    <label>
                        Select a Category:
                        <select value={selectedCategory} onChange={handleCategoryChange}>
                            {categories.map(category => (
                                <option key={category} value={category}>{category}</option>
                            ))}
                        </select>
                    </label>
                    Category: {selectedCategory}
                </div>
                <div>
                    <label>
                        Select a Model:
                        <select value={selectedModel} onChange={handleModelChange}>
                            {models.map(model => (
                                <option key={model} value={model}>{model}</option>
                            ))}
                        </select>
                    </label>
                    MODEL: {selectedModel}
                </div>
                <div>
                    <button type="submit">Submit</button>
                </div>
            </form>
        </div>
    );
};

export default Setup;
