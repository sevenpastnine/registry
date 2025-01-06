import { customAlphabet } from 'nanoid';

// Keep the alphabet and length in sync with the one on the backend (registry/models.py)
export default customAlphabet('23456789abcdefghjklmnpqrstuvwxyz', 12)
