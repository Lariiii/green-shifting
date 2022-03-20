import React from 'react';
import { useSelector } from 'react-redux';

const Clock = () => {

  const ts = useSelector(state => state.data.timestamp);

  return (
    <p>
      { new Date(ts).getHours().toString().padStart(2, '0')}:{ new Date(ts).getMinutes().toString().padStart(2, '0') }
    </p>
  );
};

export default Clock;