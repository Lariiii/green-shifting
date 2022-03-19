import React from 'react';
import styled from 'styled-components';

import SharedHeader from '../components/sharedheader';
import OpenPositionsBadge from '../components/openpositionsbadge';

const logo = resolvePath('images/electricitymap-logo.svg');

const headerLinks = [
  {
    label: 'Live',
    active: true,
  },
  {
    label: 'Github',
    href: 'https://github.com/Lariiii/green-shifting',
  },
];

const Container = styled.div`
  /* This makes sure the map and the other content doesn't
  go under the SharedHeader which has a fixed position. */
  height: 58px;
  @media (max-width: 767px) {
    display: none !important;
  }
`;

const Header = () => (
  <Container>
    <SharedHeader logo={logo} links={headerLinks} />
  </Container>
);

export default Header;
