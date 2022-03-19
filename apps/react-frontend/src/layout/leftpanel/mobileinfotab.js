/* eslint-disable jsx-a11y/anchor-is-valid */
/* eslint-disable jsx-a11y/anchor-has-content */
/* eslint-disable react/jsx-no-target-blank */
// TODO: re-enable rules

import React, { useState, useEffect } from 'react';
import { Redirect, useLocation } from 'react-router-dom';
import styled from 'styled-components';

import { __ } from '../../helpers/translation';
import { useIsMediumUpScreen } from '../../hooks/viewport';
import FAQ from '../../components/faq';
import ColorBlindCheckbox from '../../components/colorblindcheckbox';

const SocialButtons = styled.div`
  @media (min-width: 768px) {
    display: none !important;
  }
`;

const MobileInfoTab = () => {
  const isMediumUpScreen = useIsMediumUpScreen();
  const location = useLocation();
  const [mobileAppVersion, setMobileAppVersion] = useState(null);

  // Check app version once
  useEffect(() => {
    if (!mobileAppVersion && window.isCordova) {
      codePush.getCurrentPackage((localPackage) => {
        if (!localPackage) {
          console.log('CodePush: No updates have been installed yet');
          setMobileAppVersion(null);
          return;
        }

        const {
          appVersion, // The native version of the application this package update is intended for.
          description, // same as given during deployment
          // isFirstRun, // flag indicating if the current application run is the first one after the package was applied.
          label, // The internal label automatically given to the update by the CodePush server, such as v5. This value uniquely identifies the update within it's deployment
        } = localPackage;

        setMobileAppVersion(`${appVersion} ${label} (${description})`);
      }, err => console.error(err));
    }
  }, []);

  // If not on small screen, redirect to the /map page
  if (isMediumUpScreen) {
    return <Redirect to={{ pathname: '/map', search: location.search }} />;
  }

  return (
    <div className="mobile-info-tab">

      <div className="info-text">
        <ColorBlindCheckbox />
        { mobileAppVersion ? (
          <p>{`App version: ${mobileAppVersion}`}</p>
        ) : null}
        <p>
          {__('panel-initial-text.thisproject')}
          {' '}
          <a href="https://github.com/tmrowco/electricitymap-contrib" target="_blank">{__('panel-initial-text.opensource')}</a>
          {' '}
(
          {__('panel-initial-text.see')}
          {' '}
          <a href="https://github.com/tmrowco/electricitymap-contrib#data-sources" target="_blank">{__('panel-initial-text.datasources')}</a>
).
          {' '}
          <span dangerouslySetInnerHTML={{ __html: __('panel-initial-text.contribute', 'https://github.com/tmrowco/electricitymap-contrib/wiki/Getting-started') }} />
.
        </p>
        <p>
          {__('footer.foundbugs')}
          {' '}
          <a href="https://github.com/tmrowco/electricitymap-contrib/issues/new" target="_blank">{__('footer.here')}</a>
.
          <br />
        </p>
      </div>
      <SocialButtons className="social-buttons">
        <div>
          { /* Facebook share */}
          <div
            className="fb-share-button"
            data-href="https://app.electricitymap.org/"
            data-layout="button_count"
          />
          { /* Twitter share */}
          <a
            className="twitter-share-button"
            data-url="https://app.electricitymap.org"
            data-via="electricitymap"
            data-lang={locale}
          />
          { /* Slack */}
          <span className="slack-button">
            <a href="https://slack.tmrow.com" target="_blank" className="slack-btn">
              <span className="slack-ico" />
              <span className="slack-text">Slack</span>
            </a>
          </span>
        </div>
      </SocialButtons>

      <div className="mobile-faq-header">
        {__('misc.faq')}
      </div>
      <FAQ className="mobile-faq" />
    </div>
  );
};

export default MobileInfoTab;
