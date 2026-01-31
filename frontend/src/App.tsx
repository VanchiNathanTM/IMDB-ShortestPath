import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import AsyncSelect from 'react-select/async';

// --- Styled Components ---
const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 4rem 2rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #333;
  background-color: #fff;
  min-height: 100vh;
`;

const SearchContainer = styled.div`
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  margin-bottom: 3rem;
`;

const SearchRow = styled.div`
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  
  & > div {
    flex: 1;
  }

  @media (max-width: 600px) {
    flex-direction: column;
    gap: 1rem;
  }
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.9rem;
  color: #495057;
`;

const ButtonContainer = styled.div`
  text-align: right;
`;

const SearchButton = styled.button<{ disabled?: boolean }>`
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 4px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.65 : 1};
  font-weight: 500;
  transition: background-color 0.15s ease-in-out;

  &:hover:not(:disabled) {
    background-color: #0056b3;
  }
`;

const ResultHeader = styled.div`
  text-align: center;
  margin-bottom: 2rem;
  
  h3 {
    margin: 0 0 0.5rem 0;
    color: #6c757d;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
  }

  .degrees {
    font-size: 3rem;
    font-weight: 300;
    color: #212529;
    line-height: 1;
  }
`;

const FlowContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 500px;
  margin: 0 auto;
`;

const StepWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
`;

const StepCard = styled.div`
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem 1.5rem;
  width: 100%;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  position: relative;
  z-index: 1;
`;

const StepName = styled.div`
  font-size: 1.1rem;
  font-weight: 500;
  color: #212529;
  margin-bottom: 0.25rem;
`;

const StepType = styled.div`
  font-size: 0.8rem;
  color: #868e96;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Connector = styled.div`
  height: 2rem;
  width: 1px;
  background-color: #dee2e6;
  position: relative;
  
  &:after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #dee2e6;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  color: #6c757d;
  padding: 2rem;
  font-size: 1.1rem;
`;

// --- Types ---
interface Option {
  value: string;
  label: string;
}

interface PathStep {
  type: 'person' | 'movie';
  name: string;
  id: string;
}

interface PathResponse {
  path_found: boolean;
  degrees: number | null;
  hops: number;
  steps: PathStep[];
}

// --- Configuration ---
const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8001').trim().replace(/\/+$/, '');

// --- App Component ---
function App() {
  const [startNode, setStartNode] = useState<Option | null>(null);
  const [endNode, setEndNode] = useState<Option | null>(null);
  const [result, setResult] = useState<PathResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Search API
  const loadOptions = async (inputValue: string) => {
    if (!inputValue || inputValue.length < 2) return [];
    try {
      const res = await axios.get(`${API_URL}/search`, {
        params: { q: inputValue },
      });

      return res.data.map((item: any) => {
        const value = `${item.type}:${item.id}`;
        if (item.type === 'person') {
          return {
            value,
            label: `${item.name}${item.born ? ` (b. ${item.born})` : ''}`
          };
        }
        return {
          value,
          label: `${item.name}${item.year ? ` (${item.year})` : ''}`
        };
      });
    } catch (error) {
      console.error("Search failed:", error);
      return [];
    }
  };

  // Find Path API
  const findPath = async () => {
    if (!startNode || !endNode) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await axios.get(`${API_URL}/path`, {
        params: { start: startNode.value, end: endNode.value },
      });
      setResult(res.data);
    } catch (error) {
      console.error("Path search failed:", error);
      alert("Failed to fetch path");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <SearchContainer>
        <SearchRow>
          <div>
            <Label>Start Node</Label>
            <AsyncSelect 
              cacheOptions
              defaultOptions
              loadOptions={loadOptions}
              onChange={(newValue: any) => setStartNode(newValue)}
              placeholder="Search person or movie..."
              isClearable
            />
          </div>
          <div>
            <Label>Target Node</Label>
            <AsyncSelect 
              cacheOptions
              defaultOptions
              loadOptions={loadOptions}
              onChange={(newValue: any) => setEndNode(newValue)}
              placeholder="Search person or movie..."
              isClearable
            />
          </div>
        </SearchRow>
        <ButtonContainer>
          <SearchButton 
            onClick={findPath} 
            disabled={!startNode || !endNode || loading}
          >
            {loading ? 'Searching...' : 'Find Connection'}
          </SearchButton>
        </ButtonContainer>
      </SearchContainer>

      {result && (
        <>
          {result.path_found ? (
            <div>
              <ResultHeader>
                <h3>Degrees of Separation</h3>
                <div className="degrees">{result.degrees !== null ? result.degrees : result.hops}</div>
              </ResultHeader>
              
              <FlowContainer>
                {result.steps.map((step, index) => (
                  <StepWrapper key={index}>
                    <StepCard>
                      <StepName>{step.name}</StepName>
                      <StepType>{step.type}</StepType>
                    </StepCard>
                    {index < result.steps.length - 1 && <Connector />}
                  </StepWrapper>
                ))}
              </FlowContainer>
            </div>
          ) : (
            <EmptyState>No connection found between these two nodes.</EmptyState>
          )}
        </>
      )}
    </Container>
  );
}

export default App;
