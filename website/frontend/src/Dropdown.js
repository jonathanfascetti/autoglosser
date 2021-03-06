import * as React from 'react';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';

export default function Dropdown({ambiguity, index, ambOptions, handleChangeParent, pastAmb}) {
  const [options, setValue] = React.useState('');

  const handleChange = (event) => {
    handleChangeParent(event);
    setValue(event.target.value);
  };

  if(ambiguity === 0) {
    return (null);
  }

  return (
    <FormControl style={{ minWidth: '250px'}}>
      <FormLabel style={{color: 'white'}}>Ambiguity Options for Word {index}</FormLabel>
      <RadioGroup
        value={options}
        onChange={handleChange}
      >
        {
          [...Array(ambiguity)].map((e, i) => <FormControlLabel value={index+":"+i} control={<Radio />} label={ambOptions[index + i + pastAmb]} />)
        }
      </RadioGroup>
    </FormControl>
  );
}