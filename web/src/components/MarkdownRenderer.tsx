import { Box, List, ListItem, ListItemText, Typography } from '@mui/material';
import React from 'react';
import ReactMarkdown from 'react-markdown';

type MarkdownRendererProps = {
  content: string;
};

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <Box
      sx={{
        '& h1': { typography: 'h5', mt: 2, mb: 1 },
        '& h2': { typography: 'h6', mt: 2, mb: 1 },
        '& h3': { typography: 'subtitle1', mt: 2, mb: 1 },
        '& p': { typography: 'body1', mb: 1.5 },
      }}
    >
      <ReactMarkdown
        components={{
          h1: ({ children }) => <Typography variant="h5">{children}</Typography>,
          h2: ({ children }) => <Typography variant="h6">{children}</Typography>,
          h3: ({ children }) => <Typography variant="subtitle1">{children}</Typography>,
          p: ({ children }) => (
            <Typography variant="body1" color="text.primary" paragraph>
              {children}
            </Typography>
          ),
          ul: ({ children }) => <List sx={{ listStyleType: 'disc', pl: 4 }}>{children}</List>,
          li: ({ children }) => (
            <ListItem sx={{ display: 'list-item', py: 0.25 }}>
              <ListItemText primary={children} />
            </ListItem>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </Box>
  );
};

export default MarkdownRenderer;
