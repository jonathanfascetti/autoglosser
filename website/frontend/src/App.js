import logo from './BostonUniversityLogo.png';
import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import SearchBar from "material-ui-search-bar";
import { Text } from "react-native";
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
// import Dropdown from "./Dropdown"

function App() {
  // Stores values of the search bar
  const [searched, setSearched] = useState("");
  // Stores values of the arguments
  const [options, setOptions] = useState("");
  // Stores results of the search
  const [getMessage, setGetMessage] = useState({})

  // Processes a new search
  const requestSearch = (searchedVal) => {
    if (!searchedVal || !searchedVal.length) {
      cancelSearch();
    } else {
      setSearched(searchedVal);

      axios.post('http://localhost:5000/hello', {
          message: searchedVal,
          type: options
        }).then(response => {
          setGetMessage(response);
          console.log(response.data.message);
        }).catch(error => {
          console.log(error);
        })
    }
  };

  const handleChange = (event) => {
    setOptions(event.target.value);
  };

  // Processes a cancelled search
  const cancelSearch = () => {
    setSearched("");
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" style={{position: "absolute"}}/>
        
        <p>Moore Autoglossar</p>
        
        <SearchBar
          value={searched}
          onRequestSearch={(searchVal) => requestSearch(searchVal)}
          onCancelSearch={() => cancelSearch()}
          className="App-searchbar"
        />

        {/* <SearchBar
          value={options}
          onRequestSearch={(optionsVal) => setOptions(optionsVal)}
          onCancelSearch={() => setOptions("")}
          className="App-searchbar"
        /> */}

        {/* Displays results */}
        <div className="App-searchresults">
          {(getMessage.status === 200 && searched.length) ? 
          <Text style={{color: 'white', fontSize: 20, textAlign: 'right'}}>{getMessage.data.message}</Text>
          :
          <h3></h3>
          }
        </div>

        <FormControl>
          <FormLabel style={{color: 'white'}}>Ambiguity Options</FormLabel>
          <RadioGroup
            value={options}
            onChange={handleChange}
          >
            <FormControlLabel value="-a 3:0" control={<Radio />} label="0" />
            <FormControlLabel value="-a 3:1" control={<Radio />} label="1" />
          </RadioGroup>
        </FormControl>
      </header>
    </div>
  );
}

export default App;