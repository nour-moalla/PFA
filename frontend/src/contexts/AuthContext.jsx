import { createContext, useContext, useEffect, useState } from 'react'
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  sendSignInLinkToEmail,
  isSignInWithEmailLink,
  signInWithEmailLink,
  GoogleAuthProvider,
  signInWithPopup,
  updateProfile,
} from 'firebase/auth'
import { auth } from '../config/firebase'

const AuthContext = createContext({})

export const useAuth = () => useContext(AuthContext)

export const AuthContextProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUser({
          uid: user.uid,
          email: user.email,
          displayName: user.displayName,
          photoURL: user.photoURL,
        })
      } else {
        setUser(null)
      }
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])


  const signup = async (email, password, displayName) => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password)
      if (displayName) {
        await updateProfile(userCredential.user, { displayName })
      }
      return { success: true, user: userCredential.user }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const login = async (email, password) => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      return { success: true, user: userCredential.user }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const logout = async () => {
    try {
      await signOut(auth)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const resetPassword = async (email) => {
    try {
      await sendPasswordResetEmail(auth, email, {
        url: `${window.location.origin}/login`,
        handleCodeInApp: false,
      })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const sendSignInLink = async (email) => {
    try {
      const actionCodeSettings = {
        url: `${window.location.origin}/login`,
        handleCodeInApp: true,
      }
      await sendSignInLinkToEmail(auth, email, actionCodeSettings)
      window.localStorage.setItem('emailForSignIn', email)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const signInWithGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider()
      const userCredential = await signInWithPopup(auth, provider)
      return { success: true, user: userCredential.user }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signup,
        login,
        logout,
        resetPassword,
        sendSignInLink,
        signInWithGoogle,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

