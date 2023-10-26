import React from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'

const Documents = ({documentName,display}) => {
   const fichier = documentName.split('/').pop()
   const extension = documentName.substring(documentName.length -4)
   let documentIcon = ''
   switch (extension) {
    case 'docx':
        documentIcon = '/word.png'
        break;
    case '.pdf':
        documentIcon = '/pdf-icon.jpg'    
        break;
    default:
        break;
   }
   const documentStyle = {
    width: "100%",
    marginTop: "10px",
    border: "1px solid",
    textAlign:"center"
  }
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

    return (
        <div className={display}> 
                <div className="context" style={documentStyle}>
                    <div className='paragraph-block'>
                      <Link onClick={() => download({documentName})}> {`${fichier.substring(0, 30)}...`}
                      <p><img className='login-logo' width={50} src={documentIcon} alt='logo'></img></p>
                       </Link>
                    </div>
                 </div>
        </div>
    );
};

export default Documents;