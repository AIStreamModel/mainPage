import React, { useState } from 'react';
import SidebarMenu from './components/SidebarMenu';
import LivePageContainer from './containers/LivePageContainer';

function App() {
  const [expanded, setExpanded] = useState(true);

  const toggleSidebar = () => {
    setExpanded((prev) => !prev);
  };

  return (
    <>
      <SidebarMenu expanded={expanded} toggleSidebar={toggleSidebar} />
      <LivePageContainer expanded={expanded} />
    </>
  );
}

export default App;
