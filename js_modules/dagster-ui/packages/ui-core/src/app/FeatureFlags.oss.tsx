export enum FeatureFlag {
  flagDebugConsoleLogging = 'flagDebugConsoleLogging',
  flagDisableWebsockets = 'flagDisableWebsockets',
  flagSidebarResources = 'flagSidebarResources',
  flagDisableAutoLoadDefaults = 'flagDisableAutoLoadDefaults',
  flagSelectionSyntax = 'flagSelectionSyntax-always-on',
  flagAssetSelectionWorker = 'flagAssetSelectionWorker',
  flagUseNewObserveUIs = 'flagUseNewObserveUIs',
  flagMarketplace = 'flagMarketplace',
  flagDocsInApp = 'flagDocsInApp',

  // Flags for tests
  __TestFlagDefaultNone = '__TestFlagDefaultNone',
  __TestFlagDefaultTrue = '__TestFlagDefaultTrue',
  __TestFlagDefaultFalse = '__TestFlagDefaultFalse',
}
