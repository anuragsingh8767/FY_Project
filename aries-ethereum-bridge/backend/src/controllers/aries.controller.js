import ariesService from '../services/aries.service.js';

// Get agent status
export const getStatus = async (req, res, next) => {
  try {
    const status = await ariesService.getStatus();
    res.status(200).json(status);
  } catch (error) {
    next(error);
  }
};

// Get connections
export const getConnections = async (req, res, next) => {
  try {
    const connections = await ariesService.getConnections();
    res.status(200).json(connections);
  } catch (error) {
    next(error);
  }
};

// Create schema
export const createSchema = async (req, res, next) => {
  try {
    const { name, version, attributes } = req.body;
    
    if (!name || !version || !attributes || !Array.isArray(attributes)) {
      return res.status(400).json({ message: 'Invalid schema data' });
    }
    
    const schema = await ariesService.createSchema(name, version, attributes);
    res.status(201).json(schema);
  } catch (error) {
    next(error);
  }
};

// Create credential definition
export const createCredentialDefinition = async (req, res, next) => {
  try {
    const { schemaId, tag } = req.body;
    
    if (!schemaId) {
      return res.status(400).json({ message: 'Schema ID is required' });
    }
    
    const credentialDefinition = await ariesService.createCredentialDefinition(schemaId, tag);
    res.status(201).json(credentialDefinition);
  } catch (error) {
    next(error);
  }
};