

const saveToken =(token) =>{
    localStorage.setItem('REACT_TOKEN_AUTH_KEY', token)
}

const logout = () => {
    localStorage.removeItem('REACT_TOKEN_AUTH_KEY')
}

const isLogged = () => {
    let token = localStorage.getItem('REACT_TOKEN_AUTH_KEY')

    return !!token
}

export const authService = {
    saveToken,
    logout,
    isLogged
}