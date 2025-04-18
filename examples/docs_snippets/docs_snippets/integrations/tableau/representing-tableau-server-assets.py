from dagster_tableau import TableauServerWorkspace, load_tableau_asset_specs

import dagster as dg

# Connect to Tableau Server using the connected app credentials
tableau_workspace = TableauServerWorkspace(
    connected_app_client_id=dg.EnvVar("TABLEAU_CONNECTED_APP_CLIENT_ID"),
    connected_app_secret_id=dg.EnvVar("TABLEAU_CONNECTED_APP_SECRET_ID"),
    connected_app_secret_value=dg.EnvVar("TABLEAU_CONNECTED_APP_SECRET_VALUE"),
    username=dg.EnvVar("TABLEAU_USERNAME"),
    site_name=dg.EnvVar("TABLEAU_SITE_NAME"),
    server_name=dg.EnvVar("TABLEAU_SERVER_NAME"),
)

tableau_specs = load_tableau_asset_specs(tableau_workspace)
defs = dg.Definitions(assets=[*tableau_specs], resources={"tableau": tableau_workspace})
