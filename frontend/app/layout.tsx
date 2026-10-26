import './style.css';
import {connection} from 'next/server';
export const metadata = {title:'Python Academy',description:'A little practice. A world of possibilities.'};
// Every page renders per request, so each gets the nonce proxy.ts made for it (SEC-09).
export default async function Layout({children}:{children:React.ReactNode}) {await connection();return <html lang="en"><body><a className="skip" href="#main">Skip to content</a>{children}</body></html>}
