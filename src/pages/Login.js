import React from 'react';
import { useState } from 'react';
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom';
import { authService } from '../Services/auth.services';

const Login = () => {
  const {register, handleSubmit, formState:{errors}} = useForm()
  const navigate = useNavigate()
  const [login,setLogin] = useState("btn btn-primary loginshow")
  const [loader,setLoader] = useState("btn btn-primary btn-loaderhide")
  const [wrongcred,setWrongcred] = useState("credential")
  const [logged,setLogged] = useState(false)
  const [empty,setEmpty] = useState('show-field')
  const handleChange = (e) =>{
    setWrongcred("updating-credential")
    setEmpty('empty-field')
  }
  const loginUser = (data)=>{
    setLoader("btn btn-primary btn-loadershow")
    setLogin("btn btn-primary loginhide")
    console.log(data)
    const requestVariables ={
      method : "POST",
      headers : {
        'Content-Type':'application/json'
      },
      body : JSON.stringify(data)
    }
    fetch('http://127.0.0.1:5003/login', requestVariables)
    .then(res=>res.json())
    .then(data=>{
      console.log(data)
      if (data.access_token === undefined) {
        setLogged(true)
        setLoader("btn btn-primary btn-loaderhide")
        setLogin("btn btn-primary loginshow")
        setWrongcred('wrong-credential')
      } else {
        console.log(data.access_token)
        authService.saveToken(data.access_token)
        console.log("connexion réussi")
        navigate('/home')
      }
     
    })
    console.log(requestVariables)
    //reset()
  }

    return (
      <div className='login'>
        <div className='container'>
        <img className='login-logo' width={250} src='/lincoln.png' alt='logo'></img>
        </div>
          <div className='container welcome'> 
             <h4> Bienvenue sur la plate forme de la recherche intelligente</h4>
          </div>

          <div className='auth-wrapper'>
            <div className='auth-inner'>
          <form >
             <h3>Identifiez-vous</h3>
              <div className="mb-3">
                  <label>Username :</label>
                  <input
                    type="text"
                    id = "username"
                    className="form-control"
                    placeholder="saisir le username"
                    {...register('username',{required:true})}
                    onChange={handleChange}/>
              </div>
              {errors.username && <p className={empty} style={{color:'red'}}><small>Le champ username est obligatoire</small></p>}
              <div className="mb-3">
                  <label>Password :</label>
                  <input
                    id="password"
                    className="form-control"
                    placeholder="saisir le password"
                    type='password'
                    {...register('password',{required:true})} 
                    onChange={handleChange}/>
              </div>
              {errors.password && <p className={empty} style={{color:'red'}}><small>Le champ password est obligatoire</small></p>}
              <div className="mb-3">
              {logged ? <p className={wrongcred} style={{color:'red'}}><small>Le username ou mot de passe est incorrect</small></p> : <p className={wrongcred} style={{color:'red'}}><small>Le username ou mot de passe est incorrect</small></p>}
              </div>
              <div className="d-grid">
                  <button type="submit" className={login} onClick={handleSubmit(loginUser)} >
                      Connexion
                  </button>
                  <button className={loader} type="button" disabled>
                    <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span className="sr-only loading">Loading...</span>
                  </button>
              </div>
             
          </form>
          </div>
          </div>

      </div>
    );
};

export default Login;