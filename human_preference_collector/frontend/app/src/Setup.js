import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';  // Import useNavigate for navigation
import axios from 'axios'; // Import axios for making HTTP requests

const Setup = () => {
  const categories = ["paper", "product"];
  const models = ["gpt3_5", "gpt4"];
  const [selectedCategory, setSelectedCategory] = useState(categories[0]);
  const [selectedModel, setSelectedModel] = useState(models[0]);
  const navigate = useNavigate(); // Initialize useNavigate for redirection

  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
  };

  const handleModelChange = (event) => {
    setSelectedModel(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault(); // Prevent the default form submission behavior

    // clear the localstorage
    localStorage.clear();

    try {
      const response = await axios.post('http://localhost:5000/descriptions', {
        category: selectedCategory,
        model: selectedModel
      });
      if (response.data && response.data.length > 0) {
        // Store the data in local storage or manage via context
        localStorage.setItem('descriptions', JSON.stringify(response.data));
        navigate('/comparisons'); // Navigate to the description display route
      } else {
        console.error('No data received from the server');
        return <div>No data received from the server. Reload page and try again</div>
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      // Handle errors here, such as displaying a message to the user
      return <div>Error submitting form. Reload page and try again</div>
    }  };

  return (
    <div>
      <h1>Setup Configuration</h1>
      <form onSubmit={handleSubmit}>
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
