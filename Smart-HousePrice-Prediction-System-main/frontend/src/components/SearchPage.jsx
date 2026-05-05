import { useState } from 'react'
import Header from './Header'
import SearchPanel from './SearchPanel'
import ResultsPanel from './ResultsPanel'
import { parseUserInput, searchHouses } from '../api'
import './SearchPage.css'

const STATES = ['Andhra Pradesh', 'Delhi', 'Gujarat', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'West Bengal']

const CITIES = {
  'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Tirupati'],
  'Delhi': ['New Delhi', 'Dwarka', 'Rohini', 'Saket', 'Lajpat Nagar'],
  'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
  'Karnataka': ['Bengaluru', 'Mysuru', 'Hubli', 'Mangaluru'],
  'Kerala': ['Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Thrissur'],
  'Madhya Pradesh': ['Bhopal', 'Indore', 'Jabalpur', 'Gwalior'],
  'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Thane', 'Navi Mumbai'],
  'Punjab': ['Chandigarh', 'Ludhiana', 'Amritsar', 'Jalandhar'],
  'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota'],
  'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tiruchirappalli'],
  'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar'],
  'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Noida', 'Ghaziabad'],
  'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Siliguri']
}

export default function SearchPage() {
  const [state, setState] = useState('')
  const [city, setCity] = useState('')
  const [profile, setProfile] = useState('balanced')
  const [maxPrice, setMaxPrice] = useState(2000)
  const [promptInput, setPromptInput] = useState('')
  const [uiMode, setUiMode] = useState('form') // 'form' or 'prompt'
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async () => {
    setLoading(true)
    setError(null)

    try {
      let payload

      if (uiMode === 'prompt') {
        if (!promptInput.trim()) {
          setError('Please enter a search query')
          setLoading(false)
          return
        }
        // Use helper from api.js
        payload = await parseUserInput(promptInput)
      } else {
        if (!state || !city) {
          setError('Please select state and city')
          setLoading(false)
          return
        }

        const profileFeatures = {
          'cheap_but_safe': ['affordable', 'safe', 'near schools'],
          'balanced': ['near parks', 'near schools', 'near hospitals'],
          'premium': ['near parks', 'near schools', 'near hospitals', 'premium']
        }

        // Use helper from api.js to geocode and parse
        payload = await parseUserInput(`${profileFeatures[profile].join(', ')} in ${city}, ${state}`)
      }

      // Use helper from api.js to search
      const data = await searchHouses(payload)
      
      let resultsArr = []
      if (Array.isArray(data)) resultsArr = data
      else if (Array.isArray(data.results)) resultsArr = data.results
      else if (Array.isArray(data.data)) resultsArr = data.data
      setResults(resultsArr)
    } catch (err) {
      console.error("Search Error:", err)
      setError(err?.message || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="search-page">
      <div className="noise"></div>
      <div className="container">
        <Header />
        <SearchPanel
          stateValue={state}
          cityValue={city}
          profile={profile}
          maxPrice={maxPrice}
          states={STATES}
          cities={CITIES}
          setState={setState}
          setCity={setCity}
          setProfile={setProfile}
          setMaxPrice={setMaxPrice}
          promptInput={promptInput}
          setPromptInput={setPromptInput}
          uiMode={uiMode}
          setUiMode={setUiMode}
          onSearch={handleSearch}
          loading={loading}
        />

        <ResultsPanel results={results} loading={loading} error={error} />
      </div>
    </div>
  )
}
