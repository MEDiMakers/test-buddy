import Style from './Header.module.css';
import { GoGraph } from "react-icons/go";
import { VscAccount } from "react-icons/vsc";

const Header = () => {
  return (
    <div className={Style.header}>
      <div className={Style.iconContainer}>
        <GoGraph className={Style.icon}/>
        <VscAccount className={Style.icon}/>
      </div>
    </div>
  );
};

export default Header;