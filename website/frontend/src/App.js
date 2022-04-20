import logo from './BostonUniversityLogo.png';
import './App.css';
import React, { useState } from 'react';
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
  const [searchResult, setSearchResult] = useState({
    response: {},
    message: [],
    ambOptions: [],
    amb: [],
    pastAmb: []
  });

  // Processes a new search
  const requestSearch = (searchedVal) => {
    if (!searchedVal || !searchedVal.length) {
      cancelSearch();
    } else {

      axios.post('http://localhost:5000/hello', {
          message: searchedVal,
          type: options
        }).then(response => {
          console.log(response.data.message);
          var str = response.data.message;
          var lines = str.split("\n");

          // Clean amb
          var clean;
          if (lines[0] === "[]") {
            clean = [""];
          } else {
            clean = lines[0].replace('[', '').replace(']', '').split(', ');
          }
          console.log(clean);
          console.log("0");
          lines.shift();

          console.log("1.5");
          var clean2 = lines[0].replace('[', '').replace(']', '').split(', ');
          clean2 = clean2.map(element => { return Number(element); });
          console.log("2");
          console.log(clean2);
          console.log("3");
          lines.shift();

          var output = [];
          var pastSum = 0;
          for(var i in clean2){
            output.push(pastSum);
            if (clean2[i] != 0) {
              pastSum = pastSum + clean2[i] - 1;
            }
          }
          console.log(output);

          console.log("Setting search result to ", response, lines, clean, clean2, output);
          setSearchResult({
            response: response,
            message: lines,
            ambOptions: clean,
            amb: clean2,
            pastAmb: output
          });
          setSearched(searchedVal);
          // console.log("Inside search result is ", response.status, searched.length, clean2.length, clean.length);
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

  const { response, message, ambOptions, amb, pastAmb } = searchResult;

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
        {/* {console.log("Search result is ", response, message, ambOptions, amb, pastAmb, searched, options)} */}
        <div className="App-searchresults">
          {(response.status === 200 && searched.length) ? 
          <div>
            <div style={{display: "flex", justifyContent: "space-around"}}>
              {amb.length === ambOptions.length ?
              <div />
              :
              amb.map((ambiguity, index) => <Dropdown  ambiguity={ambiguity} index={index} ambOptions={ambOptions} handleChangeParent={handleChange} pastAmb={pastAmb[index]}/>)}
            </div>
            <Text style={{color: 'white', fontSize: 20, textAlign: 'right'}}>{message.join('\n')}</Text>
          </div>
          :
          <div />
          }
        </div>

      </header>
    </div>
  );
}

export default App;