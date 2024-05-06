import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, Typography, Button, Grid, Box } from '@mui/material';

const Comparisons = () => {
    const [descriptions, setDescriptions] = useState([]);
    const [llm_product_description, setLlmProductDescription] = useState(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [currentDescription, setCurrentDescription] = useState(null);
    const [isHumanFirst, setIsHumanFirst] = useState(Math.random() > 0.5);
    const [userChoices, setUserChoices] = useState([]);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const initDescriptions = location.state?.descriptions;
        if (initDescriptions) {
            setDescriptions(initDescriptions);
            setCurrentDescription(initDescriptions[0]);
        }
        
    }, [location.state]);

    useEffect(() => {
        if (currentIndex < descriptions.length) {
            setCurrentDescription(descriptions[currentIndex]);
            setIsHumanFirst(Math.random() > 0.5);
            // const listings = currentDescription?.llm?.listing?.descriptions?.[0]
            const details = currentDescription?.llm?.detail?.descriptions?.[0]
            setLlmProductDescription(details)
        } else if (descriptions.length && currentIndex >= descriptions.length) {
            submitResults();
        }
    }, [currentIndex, descriptions]);

    const submitResults = async () => {
        try {
            const { name, email } = JSON.parse(localStorage.getItem('user'));
            const category = localStorage.getItem('category');
            const model = localStorage.getItem('model');
            const response = await axios.post('http://localhost:5000/results', {
                username: name,
                email: email,
                category,
                model,
                userChoices,
                totalLLMChoices: userChoices.filter(choice => choice.choice === 'llm').length,
                totalHumanChoices: userChoices.filter(choice => choice.choice === 'human').length,
                totalNoPreference: userChoices.filter(choice => choice.choice === 'none').length
            });
            console.log(response.data);
            navigate('/results', { state: { userChoices } });
        } catch (error) {
            console.error('Error submitting form:', error);
        }
    };

    const handleUserChoice = (choice) => {
        setUserChoices(prevChoices => [...prevChoices, {
            index: currentIndex,
            choice,
            description: currentDescription
        }]);
        setCurrentIndex(prevIndex => prevIndex + 1);
    };


    return (
        <Box sx={{ padding: 2 }}>
            <Typography variant="h4" gutterBottom>Comparison</Typography>
            {currentDescription ? (
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <Typography>{currentIndex + 1} / {descriptions.length}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Card variant="outlined">
                            <CardContent>
                                <Typography>
                                    {localStorage.getItem('category') === 'product' ? (
                                        "The following are product descriptions from a marketplace, what do you recommend choosing? Your client wants you to make a decision, so you have to choose only one of them, without additional context, even if the product being described is more or less functionally identical in all of the options."
                                    ) : (
                                        "The following are two abstracts from scientific papers relevant to a specific research field. Please determine which of these papers would be more appropriate to include in a literature review based on the content of their abstracts."
                                    )}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item lg={8} xs={12} container spacing={2} justifyContent="center">
                        <Grid item xs={12} sm={4}>
                            <Button
                                fullWidth
                                onClick={() => handleUserChoice(isHumanFirst ? 'human' : 'llm')}
                                variant="contained"
                                color="primary"
                            >
                                Prefer Option A (left)
                            </Button>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Button
                                fullWidth
                                onClick={() => handleUserChoice(isHumanFirst ? 'llm' : 'human')}
                                variant="contained"
                                color="secondary"
                            >
                                Prefer Option B (right)
                            </Button>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Button
                                fullWidth
                                onClick={() => handleUserChoice('none')}
                                variant="outlined"
                            >
                                No Preference
                            </Button>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Card variant="outlined">
                            <CardContent>
                                <Typography variant="h5" gutterBottom>Text Option A</Typography>
                                <Typography>
                                    {isHumanFirst
                                        ? currentDescription.human.descriptions?.[0] || currentDescription.human.abstract
                                        : JSON.stringify(currentDescription.llm.abstract || llm_product_description)
                                    }
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Card variant="outlined">
                            <CardContent>
                                <Typography variant="h5" gutterBottom>Text Option B</Typography>
                                <Typography>
                                    {isHumanFirst
                                        ? JSON.stringify(currentDescription.llm.abstract || llm_product_description)
                                        : currentDescription.human.descriptions?.[0] || currentDescription.human.abstract
                                    }
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            ) : (
                <Typography>Loading descriptions...</Typography>
            )}
        </Box>
    );
};

export default Comparisons;
