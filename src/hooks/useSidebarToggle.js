import { useState, useEffect } from 'react';

export const useSidebarToggle = () => {
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (e.clientX < 50) setExpanded(true);
      else if (e.clientX > 250) setExpanded(false);
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return { expanded, setExpanded };
};
