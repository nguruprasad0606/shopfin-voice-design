import {createContext,useContext,useEffect,useState,ReactNode} from 'react'
type Mode='light'|'dark'
const Ctx=createContext<{mode:Mode;toggle:()=>void}>({mode:'light',toggle:()=>{}})
export const useTheme=()=>useContext(Ctx)
export function ThemeProvider({children}:{children:ReactNode}){
const [mode,setMode]=useState<Mode>(()=>(localStorage.getItem('sfv-theme') as Mode)||'light')
useEffect(()=>{document.documentElement.classList.toggle('dark',mode==='dark');localStorage.setItem('sfv-theme',mode)},[mode])
return <Ctx.Provider value={{mode,toggle:()=>setMode(m=>m==='light'?'dark':'light')}}>{children}</Ctx.Provider>}
