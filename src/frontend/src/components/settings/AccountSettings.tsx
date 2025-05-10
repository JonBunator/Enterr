import { Divider, Link, Typography } from "@mui/material";
import './AccountSettings.scss';
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/16/solid";

export default function AccountSettings() {

  return (
    <div className="account-settings">
      <div>
        <Typography typography="h6">Account</Typography>
        <Typography sx={{ color: 'text.secondary', fontSize: 14 }}>Settings for your account</Typography>
      </div>
      <Divider flexItem/>
      <div>
        <Typography typography="h6">Username</Typography>
        <Typography sx={{ color: 'text.secondary', fontSize: 14 }}>It's not possible to change the username. You have to create a new account.</Typography>
      </div>
      <Divider flexItem/>
      <div>
        <Typography typography="h6">Password</Typography>
        <Typography sx={{ color: 'text.secondary', fontSize: 14 }}>The password can only be changed via the terminal. See <Link rel="noopener" href="https://github.com/JonBunator/Enterr">GitHub<ArrowTopRightOnSquareIcon className="icon-small"/></Link> for more information.</Typography>
      </div>
    </div>
  );
}