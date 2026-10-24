import './style.css';
export const metadata = {title:'Python Academy',description:'A little practice. A world of possibilities.'};
export default function Layout({children}:{children:React.ReactNode}) {return <html lang="en"><body><a className="skip" href="#main">Skip to content</a>{children}</body></html>}
