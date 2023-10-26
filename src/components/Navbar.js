import React from 'react';
import {Link} from 'react-router-dom';

const Navbar = () => {
    return (
        <nav className="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
            <div className="container-fluid">
                <Link className="navbar-brand" to=""><img src="/LogoLincoln.png" width={150} alt="Logo personnalisé" /></Link>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main_nav">
                    <span className="navbar-toggler-icon"></span>
                    </button>
                <div className="collapse navbar-collapse" id="main_nav">
                    <ul className="navbar-nav ms-auto">
                       {/* <li className="nav-item"><Link className="nav-link" href="#"> <i class="fa fa-user" aria-hidden="true"></i> Utilisateur </Link></li>*/} 
                        <li className="nav-item"><Link className="nav-link" to=""> <i className="fa fa-sign-out" aria-hidden="true"></i> Déconnexion </Link></li>
                    </ul>
                </div> 
            </div> 
        </nav>
    );
};

export default Navbar;