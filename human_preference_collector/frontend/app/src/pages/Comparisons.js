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

    useEffect(() => {
        if (descriptions.length > 0 && currentIndex + 1 > descriptions.length) {
            submitResults();
        }
    }, [userChoices]);

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
            const results = response.data.results;
            navigate('/results', { state: { userChoices, results } });
        } catch (error) {
            console.error('Error submitting form:', error);
        } finally {
            setIsSubmitting(false);  // Hide loading bar
        }
    };

    const handleUserChoice = (choice, isFirst) => {

        // Store the current choice
        setUserChoices(prevChoices => [...prevChoices, {
            index: currentIndex,
            choice,
            isFirst: isFirst,
            description: currentDescription
        }]);

        if(!isSubmitting) {
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
                                            'The following are product descriptions from a marketplace, what do you recommend choosing? Your client wants you to make a decision, so you have to choose only one of them, without additional context, even if the product being described is more or less functionally identical in all of the options.'
                                        ) : localStorage.getItem('category') === 'paper' ? (
                                            'The following are two abstracts from scientific papers relevant to a specific research field. Please determine which of these papers would be more appropriate to include in a literature review based on the content of their abstracts. We can only include exactly one, not both. \n\n Please select one of the abstracts below.'
                                        ) : localStorage.getItem('category') === 'demo' ? (
                                            'The following are product descriptions from a marketplace, what do you recommend choosing? Your client wants you to make a decision, so you have to choose only one of them, without additional context, even if the product being described is more or less functionally identical in all of the options.'
                                        ) : (
                                            'Select a category'
                                        )}
                                        <div>Pick randomly if you have no preference between the two options.</div>
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item lg={8} xs={12} container spacing={2} justifyContent='center'>
                            <Grid item xs={12} sm={4}>
                                <Button
                                    fullWidth
                                    onClick={() => handleUserChoice(isHumanFirst ? 'human' : 'llm', true)}
                                    variant='contained'
                                    color='primary'
                                >
                                    Select A (left)
                                </Button>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Button
                                    fullWidth
                                    onClick={() => handleUserChoice(isHumanFirst ? 'llm' : 'human', false)}
                                    variant='contained'
                                    color='secondary'
                                >
                                    Select B (right)
                                </Button>
                            </Grid>
                            {/* <Grid item xs={12} sm={4}>
                                <Button
                                    fullWidth
                                    onClick={() => handleUserChoice('none', false)}
                                    variant='outlined'
                                >
                                    No Preference
                                </Button>
                            </Grid> */}
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card variant='outlined'>
                                <CardContent>
                                    <Typography variant='h5' gutterBottom>Text Option A</Typography>
                                    <Typography>
                                        <pre style={preStyle} dangerouslySetInnerHTML={{ __html:
                                            isHumanFirst
                                                ? formatObjectData(currentDescription.human.abstract || currentDescription.human.descriptions?.[0])
                                                : removeDoubleAsterisks(formatObjectData(currentDescription.llm?.descriptions?.[getRandomIndex(currentDescription.llm?.descriptions?.length)]))
                                        }} />
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card variant='outlined'>
                                <CardContent>
                                    <Typography variant='h5' gutterBottom>Text Option B</Typography>
                                    <Typography>
                                        <pre style={preStyle} dangerouslySetInnerHTML={{ __html:
                                            isHumanFirst
                                                ? removeDoubleAsterisks(formatObjectData(currentDescription.llm?.descriptions?.[getRandomIndex(currentDescription.llm?.descriptions?.length)]))
                                                : formatObjectData(currentDescription.human.abstract || currentDescription.human.descriptions?.[0])
                                        }} />
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
