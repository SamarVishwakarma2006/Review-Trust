import Analyzer from "./analyzer";

export default function Home() {
  return (
    <main>
      <header>
        <p className="eyebrow">Electronics · English · Experimental</p>
        <h1>ReviewTrust</h1>
        <p className="intro">Inspect the patterns behind product reviews.</p>
        <p>Observable patterns are not proven deception. A Trust Score does not verify authenticity or measure product quality.</p>
      </header>
      <Analyzer />
    </main>
  );
}
