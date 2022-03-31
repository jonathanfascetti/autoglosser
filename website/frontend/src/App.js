import logo from './BostonUniversityLogo.png';
import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import SearchBar from "material-ui-search-bar";
import { Text } from "react-native";
import Dropdown from "./Dropdown"

function App() {
  // Stores values of the search bar
  const [searched, setSearched] = useState("");
  // Stores values of the arguments
  const [options, setOptions] = useState("");
  // Stores results of the search
  const [getResponse, setResponse] = useState({});
  const [getMessage, setGetMessage] = useState([]);
  const [ambOptions, setAmbOptions] = useState([]);
  const [amb, setAmb] = useState([]);


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
          var str = response.data.message;
          var lines = str.split("\n");
          // Clean amb
          var clean = lines[0].split(' ').join('').replace('[', '').replace(']', '');
          // console.log(clean);
          setAmbOptions(clean.split(','));
          lines.shift();
          clean = lines[0].split(' ').join('').replace('[', '').replace(']', '');
          // console.log(clean);
          setAmb(clean.split(',').map(element => { return Number(element); }));
          lines.shift();

          setGetMessage(lines)
          setResponse(response);
          console.log(response.data.message);
        }).catch(error => {
          console.log(error);
        })
    }
  };

  const handleChange = (event) => {
    if (options === "") {
      setOptions("-a " + event.target.value);
    } else {
      setOptions(options + "/" + event.target.value);
    }
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

        {/* Displays results */}
        <div className="App-searchresults">
          {(getResponse.status === 200 && searched.length) ? 
          <div>
            <div>
              {amb.map((ambiguity, index) => <Dropdown ambiguity={ambiguity} index={index} ambOptions={ambOptions} handleChangeParent={handleChange}/>)}
            </div>
            <Text style={{color: 'white', fontSize: 20, textAlign: 'right'}}>{getMessage.join('\n')}</Text>
          </div>
          :
          <h3></h3>
          }
        </div>

        {/* <Dropdown ambiguity={5} index={0} handleChangeParent={handleChange}/> */}
        {/* <h3>{options}</h3> */}
      </header>
    </div>
  );
}

export default App;