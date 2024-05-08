import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { TextField, Button, MenuItem, FormControl, InputLabel, Select, Typography, Box } from '@mui/material';

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
    }, []);

    const handleUsernameChange = (event) => setUsername(event.target.value);
    const handleEmailChange = (event) => setEmail(event.target.value);
    const handleCategoryChange = (event) => setSelectedCategory(event.target.value);
    const handleModelChange = (event) => setSelectedModel(event.target.value);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!username.trim()) {
            setError('Username cannot be empty');
            return;
        }

        localStorage.clear();

        try {
            const response = await axios.post('http://localhost:5000/descriptions', {
                username, email, category: selectedCategory, model: selectedModel
            });
            if (response.data && response.data.length > 0) {
                localStorage.setItem('user', JSON.stringify({ name: username, email: email }));
                localStorage.setItem('model', selectedModel);
                localStorage.setItem('category', selectedCategory);
                navigate('/comparisons', { state: { descriptions: response.data } });
            } else {
                console.error('No data received from the server');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
        }
    };

    return (
        <Box sx={{ width: '100%', maxWidth: 500, margin: 'auto' }}>
            <Typography variant="h4" gutterBottom>Setup</Typography>
            {error && <Typography color="error">{error}</Typography>}
            <form onSubmit={handleSubmit}>
                <TextField
                    label="Username"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name="username"
                    value={username}
                    onChange={handleUsernameChange}
                />
                <TextField
                    label="Email"
                    type="email"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    name="email"
                    value={email}
                    onChange={handleEmailChange}
                />
                <FormControl fullWidth margin="normal">
                    <InputLabel>Category</InputLabel>
                    <Select
                        value={selectedCategory}
                        label="Category"
                        onChange={handleCategoryChange}
                    >
                        {categories.map((category) => (
                            <MenuItem key={category} value={category}>{category}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl fullWidth margin="normal">
                    <InputLabel>Model</InputLabel>
                    <Select
                        value={selectedModel}
                        label="Model"
                        onChange={handleModelChange}
                    >
                        {models.map((model) => (
                            <MenuItem key={model} value={model}>{model}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <Button type="submit" variant="contained" color="primary">Submit</Button>
            </form>
        </Box>
    );
};

export default Setup;