import React, { useState, useEffect } from 'react';

const TarotDeckVisualization = () => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [flippedCards, setFlippedCards] = useState([]);
  const [isReading, setIsReading] = useState(false);
  const [readingCards, setReadingCards] = useState([]);
  
  // Tarot card data
  const tarotCards = [
    { id: 0, name: "The Moon", symbol: "☾", element: "Water", interpretation: "Mystery, intuition, unconscious, illusion" },
    { id: 1, name: "The High Priestess", symbol: "Ⅱ", element: "Water", interpretation: "Hidden knowledge, mystery, inner voice" },
    { id: 2, name: "The Star", symbol: "⋆", element: "Air", interpretation: "Hope, inspiration, generosity, serenity" },
    { id: 3, name: "The Sword", symbol: "X", element: "Air", interpretation: "Courage, action, intellect, truth" },
    { id: 4, name: "The Hermit", symbol: "Ⅸ", element: "Earth", interpretation: "Introspection, solitude, guidance, wisdom" },
    { id: 5, name: "The Sleeping One", symbol: "Ⅶ", element: "Water", interpretation: "Dreams, surrender, unconscious knowledge" },
    { id: 6, name: "Balance", symbol: "Ⅺ", element: "Air", interpretation: "Harmony, equilibrium, justice, truth" },
    { id: 7, name: "The Observer", symbol: "X", element: "Fire", interpretation: "Perspective, vision, clarity, oversight" },
    { id: 8, name: "The Triangulation", symbol: "Ⅴ", element: "Earth", interpretation: "Foundation, structure, stability, construction" },
    { id: 9, name: "The Illuminated Skull", symbol: "Ⅱ", element: "Fire", interpretation: "Transformation, revelation, awakening" },
    { id: 10, name: "The Tree of Light", symbol: "Ⅰ", element: "Earth", interpretation: "Growth, abundance, connection, life force" },
    { id: 11, name: "The Contemplator", symbol: "Ο", element: "Water", interpretation: "Reflection, depth, emotional wisdom" }
  ];
  
  // Color palette based on the image
  const colors = {
    purple: '#c27fb1',
    teal: '#65d6bd',
    pink: '#ffcce6',
    yellow: '#ffeaaa',
    background: '#ffccdd'
  };
  
  // Random pastel color generator for cards
  const getPastelColor = (id) => {
    const baseColors = [colors.purple, colors.teal];
    return baseColors[id % 2];
  };
  
  // Handle card selection
  const handleCardClick = (id) => {
    if (isReading) return;
    
    if (flippedCards.includes(id)) {
      setFlippedCards(flippedCards.filter(cardId => cardId !== id));
      if (selectedCard === id) setSelectedCard(null);
    } else {
      setFlippedCards([...flippedCards, id]);
      setSelectedCard(id);
    }
  };
  
  // Start a 3-card reading
  const startReading = () => {
    setIsReading(true);
    const shuffled = [...tarotCards].sort(() => Math.random() - 0.5);
    setReadingCards(shuffled.slice(0, 3));
    setFlippedCards([]);
    setSelectedCard(null);
  };
  
  // Reset everything
  const resetDeck = () => {
    setIsReading(false);
    setFlippedCards([]);
    setSelectedCard(null);
    setReadingCards([]);
  };
  
  return (
    <div className="flex flex-col items-center min-h-screen w-full p-6" style={{ backgroundColor: colors.background }}>
      <h1 className="text-4xl font-bold mb-6 text-center" style={{ color: colors.purple }}>
        Pastel Oracle
      </h1>
      
      <div className="flex gap-4 mb-8">
        <button 
          onClick={startReading} 
          className="px-4 py-2 rounded-full font-medium"
          style={{ backgroundColor: colors.teal, color: 'white' }}
        >
          Three Card Reading
        </button>
        <button 
          onClick={resetDeck} 
          className="px-4 py-2 rounded-full font-medium"
          style={{ backgroundColor: colors.purple, color: 'white' }}
        >
          Reset Deck
        </button>
      </div>
      
      {isReading ? (
        <div className="w-full max-w-4xl">
          <h2 className="text-2xl font-semibold mb-4 text-center" style={{ color: colors.purple }}>
            Your Reading
          </h2>
          <div className="flex flex-wrap justify-center gap-4 mb-6">
            {readingCards.map((card, index) => (
              <div 
                key={card.id} 
                className="flex flex-col items-center"
              >
                <div 
                  className="w-60 h-96 rounded-xl mb-2 flex items-center justify-center cursor-pointer shadow-lg transform hover:scale-105 transition-transform"
                  style={{ 
                    backgroundColor: getPastelColor(card.id),
                    border: `4px solid ${colors.yellow}`
                  }}
                  onClick={() => handleCardClick(card.id)}
                >
                  <div className="text-center p-4">
                    <div className="text-5xl mb-2">{card.symbol}</div>
                    <h3 className="text-xl font-semibold">{card.name}</h3>
                    <div className="mt-4 text-sm">
                      Element: {card.element}
                    </div>
                    <div className="mt-4">
                      {card.interpretation}
                    </div>
                  </div>
                </div>
                <div className="text-center font-medium" style={{ color: colors.purple }}>
                  {index === 0 ? "Past" : index === 1 ? "Present" : "Future"}
                </div>
              </div>
            ))}
          </div>
          <div className="bg-white bg-opacity-70 p-6 rounded-xl">
            <h3 className="text-xl font-semibold mb-2" style={{ color: colors.purple }}>Interpretation</h3>
            <p className="mb-2">This three-card spread represents your past, present, and future energies.</p>
            <p>The combination suggests a journey through {readingCards[0]?.element}, {readingCards[1]?.element}, and {readingCards[2]?.element} energies, inviting you to consider how {readingCards[0]?.interpretation.toLowerCase()} from your past connects to {readingCards[1]?.interpretation.toLowerCase()} in your present, ultimately leading toward {readingCards[2]?.interpretation.toLowerCase()} in your future.</p>
          </div>
        </div>
      ) : (
        <div className="w-full max-w-4xl">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {tarotCards.map(card => (
              <div 
                key={card.id} 
                className={`w-full aspect-[2/3] rounded-xl flex items-center justify-center cursor-pointer shadow-lg transform hover:scale-105 transition-transform ${flippedCards.includes(card.id) ? "ring-4" : ""}`}
                style={{ 
                  backgroundColor: getPastelColor(card.id),
                  border: `3px solid ${colors.yellow}`,
                  transform: flippedCards.includes(card.id) ? "rotateY(180deg)" : "rotateY(0deg)",
                  transition: "transform 0.6s"
                }}
                onClick={() => handleCardClick(card.id)}
              >
                {flippedCards.includes(card.id) ? (
                  <div className="text-center p-2 transform rotate-180" style={{ transform: "rotateY(180deg)" }}>
                    <div className="text-3xl mb-1">{card.symbol}</div>
                    <h3 className="text-lg font-semibold">{card.name}</h3>
                    <div className="mt-2 text-xs">
                      Element: {card.element}
                    </div>
                    <div className="mt-1 text-xs">
                      {card.interpretation}
                    </div>
                  </div>
                ) : (
                  <div className="text-4xl" style={{ color: "rgba(255,255,255,0.5)" }}>✧</div>
                )}
              </div>
            ))}
          </div>
          
          {selectedCard !== null && (
            <div className="mt-8 bg-white bg-opacity-70 p-6 rounded-xl">
              <h3 className="text-2xl font-semibold mb-2" style={{ color: colors.purple }}>
                {tarotCards[selectedCard].name}
              </h3>
              <div className="flex gap-4 items-center mb-4">
                <div 
                  className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
                  style={{ backgroundColor: getPastelColor(selectedCard) }}
                >
                  {tarotCards[selectedCard].symbol}
                </div>
                <div>
                  <div className="text-sm font-medium">Element: {tarotCards[selectedCard].element}</div>
                </div>
              </div>
              <p className="mb-4">{tarotCards[selectedCard].interpretation}</p>
              <p>This card invites you to explore themes of {tarotCards[selectedCard].interpretation.toLowerCase()} in your current situation. Consider how these energies might be manifesting in your life and what guidance they offer.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TarotDeckVisualization;
