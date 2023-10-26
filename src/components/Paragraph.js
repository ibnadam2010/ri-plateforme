import React from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'
const Paragraph = ({display,context,answer,confiance, documentName}) => {
    const fichier = documentName.split('/').pop()

    const download = (path) =>{
        const token = localStorage.getItem('REACT_TOKEN_AUTH_KEY')
         console.log("le document :"+path.documentName)
         const document_path = 'http://127.0.0.1:5003/getdocument'+path.documentName
           axios.get(document_path,{
             responseType:'blob',
             headers:{
             Authorization: `Bearer ${token}`
         }    
         })
         .then((obj)=>{
             const filename = path.documentName
             const aTag = document.createElement('a')
             aTag.href = document_path
             aTag.setAttribute('download',filename)
             aTag.setAttribute('title',fichier)
             document.body.appendChild(aTag)
             aTag.click()
             aTag.remove()
             console.log(documentName)
         })
         .catch(err=>console.error(err))
 
 
         console.log(document_path)
     }
 
    const affichage_taux = (valeur) => {
        const taux = Math.round(valeur*100) 

        if (taux >= 70) {
            return <span><small style={{color:'green'}}><u>Indice de confiance de la réponse</u> : {taux} %</small></span> // Couleur verte foncée pour un score élevé
          } else if (taux >= 50) {
            return <span><small style={{color:'orange'}}><u>Indice de confiance de la réponse</u> : {taux} %</small></span> // Couleur orange foncée pour un score moyen
          } else {
            return <span><small style={{color:'red'}}><u>Indice de confiance de la réponse</u> : {taux} %</small></span>  // Couleur rouge foncée pour un score faible
          }
    }

    const formatResponseInContext = (context, answer) => {
        if (!context || !answer) {
          return null;
        }
    
    // Utilisez une régex pour rechercher et remplacer la réponse par la réponse formatée
        const formattedContext = context.replace(
          new RegExp(answer, "gi"), // "gi" signifie une correspondance globale et insensible à la casse
          `<mark style="padding:5px">$&</mark>`
        );
    
        return <p dangerouslySetInnerHTML={{ __html: formattedContext }} />;
      };

    return (
        <div className={display}> 
            <p className='paragraph-answer'>{answer}</p>
                <div className="context">
                    <div className='confiance-scoe'><span>{affichage_taux(confiance)}</span></div>
                    <div className='paragraph-block'> {formatResponseInContext(context,answer)}
                    <Link onClick={() => download({documentName})}>
                      <p>Télécharger le document</p>
                       </Link>
                    </div>
                 </div>
        </div>
    );
};

export default Paragraph;