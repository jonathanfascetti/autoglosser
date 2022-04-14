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
  const [pastAmb, setPastAmb] = useState([]);

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
          var clean = lines[0].replace('[', '').replace(']', '');
          setAmbOptions(clean.split(', '));
          lines.shift();
          clean = lines[0].split(' ').join('').replace('[', '').replace(']', '');
          setAmb(clean.split(',').map(element => { return Number(element); }));
          lines.shift();
          var myarray = clean.split(',').map(element => { return Number(element); });
          var output = [];
          var pastSum = 0;
          for(var i in myarray){
            output.push(pastSum)
            pastSum = pastSum + myarray[i]
          }
          setPastAmb(output);

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
        
        <p>Moore Autoglosser</p>
        
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
            <div style={{display: "flex", justifyContent: "space-around"}}>
              {amb.length === ambOptions.length ?
              <h3 />
              :
              amb.map((ambiguity, index) => <Dropdown  ambiguity={ambiguity} index={index} ambOptions={ambOptions} handleChangeParent={handleChange} pastAmb={pastAmb[index]}/>)}
            </div>
            <Text style={{color: 'white', fontSize: 20, textAlign: 'right'}}>{getMessage.join('\n')}</Text>
          </div>
          :
          <h3></h3>
          }
        </div>

      </header>
    </div>
  );
}

export default App;