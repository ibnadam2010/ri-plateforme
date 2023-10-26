import {React, useState} from 'react';
import Navbar from '../components/Navbar';
import Answer from '../components/Answer';
import {useForm} from 'react-hook-form';
import Paragraph from '../components/Paragraph';
import Documents from '../components/Documents';

const Home = () => {
    const {register, handleSubmit, formState:{errors}} = useForm()
    const [display, setDisplay] = useState("hideparagraph")
    const [reponse, setReponse] = useState("")
    const [comprehension,setComprehension] = useState(true)
    const [paragraph, setParagraph] = useState([])
    const [documents, setDocuments] = useState([])

    const postQuestion = (data)=>{
        setReponse("")
        setParagraph([])
        setDocuments([])
        const token = localStorage.getItem('REACT_TOKEN_AUTH_KEY')
        console.log(data)
        console.log(token)
        
        const requestVariables ={
            method : "POST",
            headers : {
              'Content-Type':'application/json',
              'Authorization': `Bearer ${token}`
            },
            body : JSON.stringify(data)
          }

          fetch('http://127.0.0.1:5003/research', requestVariables)
          .then(res=>res.json())
          .then(data=>{
            //si data msg existe alors token expiré sinon getdata
            if (data.msg === undefined) {
                //console.log(data.output_docs)
                if (data.output_docs === undefined ) {
                    console.log("requete compréhension")
                    console.log(data.output_answers_paragraphs.answers)
                    setComprehension(true)
                    setParagraph(data.output_answers_paragraphs.answers)
                    setReponse(data.output_gen[0].answer)
                } else {
                    setComprehension(false)
                    console.log("question requete")
                    setReponse(data.output_docs) 
                    console.log(data.output_docs)
                    setDocuments(data.output_docs)
                }
                   
            } else {
                setDisplay("hideparagraph")
                console.log(data.msg)
                setReponse("session expiré, reconnexion obligatoire") 
            }
           
          }).catch(err =>console.log(err))
    }


    return (
        <div className='container'>
            <Navbar/>
            <div className='container search-content'>
                <div className='d-flex justify-content-center align-items-center search-block'>
                <div className='under container'>
                <div className='search-form'>
                     <h4>Recherche intelligente</h4>
                     <div className='search-form'>
                        <input type="text" id='question' className="form-control" {...register('requete',{required:true})} placeholder="Avez-vous une question? Posez la ici" />
                        {errors.requete && <p style={{color:'red'}}><small>le champ saisir une question est obligatoire</small></p>}
                        <button type="button"className="btn btn-primary search" onClick={handleSubmit(postQuestion)} >Recherche</button>      
                     </div>
                </div>
                </div>
                </div>
                <div className='container search-result'>
                   {comprehension? <Answer reponse={reponse} /> :documents.map(
                        (column,index)=>(<Documents key={index} documentName={column}/>)
                   )}
                    
                    {
                              paragraph.map(
                                (ligne,index)=>(
                                  <Paragraph key ={index} display={display}  answer={ligne.answer} context={ligne.context} confiance={ligne.score} documentName={ligne.meta.document_absolute_path}/>
                                )
                              )
                     }
                    
                </div>
            </div>

        </div>
    );
};

export default Home;