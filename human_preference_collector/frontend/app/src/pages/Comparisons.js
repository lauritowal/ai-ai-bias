import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, Typography, Button, Grid, Box, LinearProgress } from '@mui/material';

function removeDoubleAsterisks(text) {
    return text?.replace(/\*\*/g, '') || '';
}

function formatObjectData(data) {
    if (typeof data === 'object' && data !== null) {
        return JSON.stringify(data, null, 2);
    }
    return data?.toString() || '';
}

function getRandomIndex(arrayLength) {
    return Math.floor(Math.random() * arrayLength);
}

const Comparisons = () => {
    const [descriptions, setDescriptions] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [currentDescription, setCurrentDescription] = useState(null);
    const [isHumanFirst, setIsHumanFirst] = useState(Math.random() > 0.5);
    const [userChoices, setUserChoices] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // Initialize descriptions from location state
        const initDescriptions = location.state?.descriptions;
        if (initDescriptions) {
            setDescriptions(initDescriptions);
            setCurrentIndex(0); // Reset index
            setCurrentDescription(initDescriptions[0]);
            setIsHumanFirst(Math.random() > 0.5);
        }
    }, [location.state]);

    const submitResults = async () => {
        setIsSubmitting(true);  // Show loading bar

        try {
            const { name, email } = JSON.parse(localStorage.getItem('user'));
            const category = localStorage.getItem('category');
            const model = localStorage.getItem('model');
            const response = await axios.post('/results', {
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
        } finally {
            setIsSubmitting(false);  // Hide loading bar
        }
    };

    const handleUserChoice = (choice) => {
        // Store the current choice
        setUserChoices(prevChoices => [...prevChoices, {
            index: currentIndex,
            choice,
            description: currentDescription
        }]);

        // Move to the next description or submit results
        if (currentIndex + 1 >= descriptions.length) {
            submitResults();
        } else {
            const nextIndex = currentIndex + 1;
            setCurrentIndex(nextIndex);
            setCurrentDescription(descriptions[nextIndex]);
            setIsHumanFirst(Math.random() > 0.5);
        }
    };

    const preStyle = {
        whiteSpace: 'pre-wrap',
        wordWrap: 'break-word'
    };

    return (
        <Box sx={{ padding: 2 }}>
            <Typography variant='h4' gutterBottom>Comparison</Typography>
            {isSubmitting ? (
                <LinearProgress />
            ) : (
                currentDescription && (
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Typography>{currentIndex + 1} / {descriptions.length}</Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Card variant='outlined'>
                                <CardContent>
                                    <Typography>
                                        {localStorage.getItem('category') === 'product' ? (
                                            'The following are product descriptions from a marketplace. What do you recommend choosing?'
                                        ) : (
                                            'The following are two abstracts from scientific papers. Please determine which would be more suitable for inclusion in a literature review.'
                                        )}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item lg={8} xs={12} container spacing={2} justifyContent='center'>
                            <Grid item xs={12} sm={4}>
                                <Button
                                    fullWidth
                                    onClick={() => handleUserChoice(isHumanFirst ? 'human' : 'llm')}
                                    variant='contained'
                                    color='primary'
                                >
                                    Select A (left)
                                </Button>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Button
                                    fullWidth
                                    onClick={() => handleUserChoice(isHumanFirst ? 'llm' : 'human')}
                                    variant='contained'
                                    color='secondary'
                                >
                                    Select B (right)
                                </Button>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Button
                                    fullWidth
                                    onClick={() => handleUserChoice('none')}
                                    variant='outlined'
                                >
                                    No Preference
                                </Button>
                            </Grid>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card variant='outlined'>
                                <CardContent>
                                    <Typography variant='h5' gutterBottom>Text Option A</Typography>
                                    <Typography>
                                        <pre style={preStyle}>
                                            {isHumanFirst
                                                ? formatObjectData(currentDescription.human.abstract || currentDescription.human.descriptions?.[0])
                                                : removeDoubleAsterisks(formatObjectData(currentDescription.llm?.descriptions?.[getRandomIndex(currentDescription.llm?.descriptions?.length)]))
                                            }
                                        </pre>
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card variant='outlined'>
                                <CardContent>
                                    <Typography variant='h5' gutterBottom>Text Option B</Typography>
                                    <Typography>
                                        <pre style={preStyle}>
                                            {isHumanFirst
                                                ? removeDoubleAsterisks(formatObjectData(currentDescription.llm?.descriptions?.[getRandomIndex(currentDescription.llm?.descriptions?.length)]))
                                                : formatObjectData(currentDescription.human.abstract || currentDescription.human.descriptions?.[0])
                                            }
                                        </pre>
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                )
            )}
        </Box>
    );
};

export default Comparisons;
