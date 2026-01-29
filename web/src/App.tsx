import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Divider,
  FormControlLabel,
  Slider,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { useMemo, useState } from 'react';
import MarkdownRenderer from './components/MarkdownRenderer';
import { streamExplanation } from './api/openrouter';
import { topics } from './data/topics';

const SLIDER_LABEL =
  "Legends: 0 = Explain like I'm five, 50 = Explain like I'm a high school student, 100 = Explain like I'm an expert in the field";

const DEFAULT_COMPLEXITY = 0;

const App = () => {
  const [topic, setTopic] = useState('');
  const [complexity, setComplexity] = useState<number>(DEFAULT_COMPLEXITY);
  const [mandarin, setMandarin] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [error, setError] = useState<string | null>(null);

  const functionUrl = useMemo(() => {
    return import.meta.env.VITE_OPENROUTER_FUNCTION_URL as string | undefined;
  }, []);

  const handleRandomTopic = () => {
    const randomTopic = topics[Math.floor(Math.random() * topics.length)];
    setTopic(randomTopic);
    setExplanation('');
    setError(null);
    setGenerating(false);
  };

  const handleExplain = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic.');
      return;
    }
    if (!functionUrl) {
      setError('Missing VITE_OPENROUTER_FUNCTION_URL configuration.');
      return;
    }

    setGenerating(true);
    setExplanation('');
    setError(null);

    try {
      await streamExplanation(
        functionUrl,
        {
          topic: topic.trim(),
          complexity,
          mandarin,
        },
        (chunk) => {
          setExplanation((prev) => prev + chunk);
        },
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate explanation.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: { xs: 4, md: 6 } }}>
      <Stack spacing={4}>
        <Box>
          <Typography variant="h3" component="h1" gutterBottom>
            ELI5++
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Enter the topic you want to learn about and choose the complexity level. I will then explain it to you at the
            selected level from the slider. The explanation can be anywhere between Explain Like I'm 5, Explain like I'm a
            high school student or Explain like I'm an expert in the field or anything in between.
          </Typography>
        </Box>

        <FormControlLabel
          control={<Switch checked={mandarin} onChange={(event) => setMandarin(event.target.checked)} />}
          label="Mandarin"
        />

        <Box>
          <Typography variant="subtitle2" gutterBottom>
            {SLIDER_LABEL}
          </Typography>
          <Slider
            value={complexity}
            onChange={(_, value) => setComplexity(value as number)}
            min={0}
            max={100}
            disabled={generating}
          />
        </Box>

        <Stack spacing={2} direction={{ xs: 'column', sm: 'row' }} alignItems={{ sm: 'center' }}>
          <TextField
            fullWidth
            label="Enter a topic"
            placeholder="Type your topic and click Explain Topic"
            value={topic}
            disabled={generating}
            onChange={(event) => setTopic(event.target.value)}
          />
          <Button
            variant="contained"
            size="large"
            onClick={handleExplain}
            disabled={generating}
            sx={{ minWidth: 160 }}
          >
            Explain Topic
          </Button>
        </Stack>

        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Or select a random topic with a click of a button:
          </Typography>
          <Button variant="outlined" onClick={handleRandomTopic} disabled={generating}>
            Random Topic 🎲
          </Button>
        </Box>

        <Divider />

        <Box sx={{ minHeight: 120 }}>
          {generating && (
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                Generating explanation...
              </Typography>
            </Stack>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {explanation ? (
            <MarkdownRenderer content={explanation} />
          ) : (
            <Typography variant="body2" color="text.secondary">
              Your explanation will appear here.
            </Typography>
          )}
        </Box>
      </Stack>
    </Container>
  );
};

export default App;
