import { useState } from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Input,
  Button,
  Text,
  Container,
  Heading,
  useToast,
} from '@chakra-ui/react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import './App.css';

interface Message {
  type: 'user' | 'bot';
  content: string;
  sql?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      type: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/process', {
        question: input,
      });

      const botMessage: Message = {
        type: 'bot',
        content: response.data.answer,
        sql: response.data.sql_query,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to process your query',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChakraProvider>
      <Container maxW="container.md" py={8}>
        <VStack spacing={8} align="stretch">
          <Heading textAlign="center">Text2SQL Chatbot</Heading>
          
          <Box
            borderWidth={1}
            borderRadius="lg"
            p={4}
            height="60vh"
            overflowY="auto"
            bg="gray.50"
          >
            {messages.map((message, index) => (
              <Box
                key={index}
                mb={4}
                p={3}
                borderRadius="md"
                bg={message.type === 'user' ? 'blue.100' : 'green.100'}
                alignSelf={message.type === 'user' ? 'flex-end' : 'flex-start'}
              >
                <Text fontWeight="bold">
                  {message.type === 'user' ? 'You' : 'Bot'}
                </Text>
                {message.sql && (
                  <Box mb={2} p={2} bg="gray.200" borderRadius="md">
                    <Text fontSize="sm" fontFamily="monospace">
                      {message.sql}
                    </Text>
                  </Box>
                )}
                {message.type === 'bot' ? (
                  <Box className="markdown-content">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </Box>
                ) : (
                  <Text>{message.content}</Text>
                )}
              </Box>
            ))}
          </Box>

          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about the database..."
                disabled={loading}
              />
              <Button
                type="submit"
                colorScheme="blue"
                isLoading={loading}
                width="full"
              >
                Send
              </Button>
            </VStack>
          </form>
        </VStack>
      </Container>
    </ChakraProvider>
  );
}

export default App; 