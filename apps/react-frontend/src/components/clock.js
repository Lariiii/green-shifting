import React from 'react';
import { useSelector } from 'react-redux';

const Clock = () => {

  const ts = useSelector(state => state.data.timestamp);

  return (
    <p id="clock">
      
    </p>
  );
};

export default Clock;