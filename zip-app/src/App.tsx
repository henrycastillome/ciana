import * as React from "react"
import { useState } from 'react';
import axios from 'axios';
import { Button, CircularProgress, Input, InputGroup } from "@chakra-ui/react";
import './App.css';

function App() {
  const [map, setMap] = useState<string | null>(null);
  const [worldMap, setWorldMap] = useState<string | null>(null); // State to hold the world map
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sheetName, setSheetName] = useState<string>(''); // State to hold the sheet name\

  const handleFileUpload = async (file: File) => {
    setIsLoading(true); // Set loading state to true

    const formData = new FormData();
    formData.append('file', file);
    formData.append('sheet_name', sheetName); // Append sheet_name to formData

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      const worldMapResponse = await axios.post('http://127.0.0.1:5000/wwmap', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });
      

      const mapBlob = new Blob([response.data], { type: 'text/html' });
      const mapURL = URL.createObjectURL(mapBlob);

      const worldMapBlob = new Blob([worldMapResponse.data], { type: 'text/html' });
      const worldMapURL = URL.createObjectURL(worldMapBlob);
      setMap(mapURL);
      setWorldMap(worldMapURL);
    } catch (error) {
      console.error('Error Uploading file: ', error);
    } finally {
      setIsLoading(false); // Set loading state back to false after request completes
    }
  };


  const handleSheetNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputSheetName = e.target.value;
    const titleCaseSheetName = toTitleCase(inputSheetName); // Convert to title case
    setSheetName(titleCaseSheetName);
  };

  const handleSubmit = () => {
    const fileInput = document.getElementById('fileInput') as HTMLInputElement;
    if (fileInput.files && fileInput.files[0]) {
      handleFileUpload(fileInput.files[0]);
    } else {
      console.error('No file selected');
    }
  };

  // Function to convert string to title case
  const toTitleCase = (str: string) => {
    return str.toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase());
  };

  return (
    <>
      <div className="App">
        <h1>Ciana's Zip Code Map</h1>
      </div>

      <div className="upload">
        <InputGroup>
        <Input variant='unstyled' id="fileInput" type="file" />
        <Input
          type="text"
          placeholder="Sheet Name"
          value={sheetName}
          onChange={handleSheetNameChange}
        />

        </InputGroup>
        
        {/* Submit Button */}
        <Button onClick={handleSubmit}>Upload and Show Map</Button>
      </div>

      {/* Map Display */}
      <div className="map">
        
        {isLoading ? (
          <div className="loader">
            <CircularProgress isIndeterminate color='green.300' />
          </div>
        ) : map && (
          <iframe src={map} title="Map by Zip Code" />
        )}
      </div>

      {/* World Map Display */}

      <div className="map">
        {isLoading ? (
          <div className="loader">
            <CircularProgress isIndeterminate color='green.300' />
          </div>
        ) : worldMap && (
          <iframe src={worldMap} title="World Map"  />
        )}
      </div>
    </>
  )
}

export default App;
