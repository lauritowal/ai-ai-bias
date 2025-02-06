import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Typography, Button, Card, CardContent, Box, Grid } from '@mui/material';

const Results = () => {
    const [userChoices, setUserChoices] = useState([]);
    const [results, setResults] = useState('');
    const [userInfo, setUserInfo] = useState({});
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        if (location.state?.userChoices) {
            setUserChoices(location.state.userChoices);

            // Assuming user info is stored in local storage for the session
            const userData = JSON.parse(localStorage.getItem('user'));
            const category = localStorage.getItem('category');
            const model = localStorage.getItem('model');
            if (userData && category && model) {
                setUserInfo({
                    username: userData.name,
                    email: userData.email,
                    category,
                    model
                });
            }
        } else {
            console.error("No user choices found in location state");
        }
    }, [location.state]);

    const downloadResults = () => {
        // Prepare a filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `experiment_results_${timestamp}.json`;

        const data = location.state.results;

        // Create a Blob with the JSON data and trigger a download
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <Box sx={{ padding: 4 }}>
            <Typography variant="h4" gutterBottom>Results</Typography>

            <Button
                variant="contained"
                color="primary"
                onClick={() => navigate("/")}
                sx={{ marginBottom: 2 }}
            >
                Run another experiment
            </Button>
            <br />
            <Button
                variant="contained"
                color="secondary"
                onClick={downloadResults}
                sx={{ marginBottom: 4 }}
            >
                Download Results as JSON
            </Button>

            {/* Displaying user info */}
            <Grid container spacing={2} sx={{ marginBottom: 4 }}>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Username</Typography>
                            <Typography>{userInfo.username}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Email</Typography>
                            <Typography>{userInfo.email}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Category</Typography>
                            <Typography>{userInfo.category}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Model</Typography>
                            <Typography>{userInfo.model}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            <Typography variant="h5" gutterBottom>Total Results</Typography>
            <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Preference of Human text</Typography>
                            <Typography>{userChoices.filter(choice => choice.choice === 'human').length}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Preference of LLM text</Typography>
                            <Typography>{userChoices.filter(choice => choice.choice === 'llm').length}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">No Preference</Typography>
                            <Typography>{userChoices.filter(choice => choice.choice === 'none').length}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            <Typography variant="h5" gutterBottom mt={4}>Individual Choices</Typography>
            {userChoices.map((choice, index) => (
                <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                        <Typography variant="h6">Choice {index + 1}</Typography>
                        <Typography>Chosen option: {choice.choice}</Typography>
                        <Typography>Title: {choice.description.human.title}</Typography>
                        <Typography>isFirst: {"" + choice.isFirst}</Typography>
                    </CardContent>
                </Card>
            ))}
        </Box>
    );
};

export default Results;
