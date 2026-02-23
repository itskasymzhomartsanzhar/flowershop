import React, { useState } from 'react';
import Menu from '../components/Menu/Menu';
import ProfileNavbar from '../components/ProfileNavbar/ProfileNavbar';
import Orders from '../components/Orders/Orders';
import Notifications from '../components/Notifications/Notifications';

const Profile = () => {

  return (
    <>
      <ProfileNavbar />
      <Notifications />
      <Orders />
    </>
  );
};

export default Profile;