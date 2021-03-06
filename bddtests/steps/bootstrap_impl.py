# Copyright IBM Corp. 2016 All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import bdd_test_util
import bootstrap_util
import orderer_util
import time

class ChannelCreationInfo:
    'Used to store the information needed to construct Config TX for orderer broadcast to create a new channel'
    def __init__(self, channelId, channelCreationPolicyName, signedConfigEnvelope):
        self.channelId = channelId
        self.channelCreationPolicyName = channelCreationPolicyName
        self.signedConfigEnvelope = signedConfigEnvelope



@given(u'the orderer network has organizations')
def step_impl(context):
    assert 'table' in context, "Expected table of orderer organizations"
    directory = bootstrap_util.getDirectory(context)
    for row in context.table.rows:
        org = directory.getOrganization(row['Organization'], shouldCreate = True)
        org.addToNetwork(bootstrap_util.Network.Orderer)


@given(u'user requests role of orderer admin by creating a key and csr for orderer and acquires signed certificate from organization')
def step_impl(context):
    assert 'table' in context, "Expected table with triplet of User/Orderer/Organization"
    directory = bootstrap_util.getDirectory(context)
    for row in context.table.rows:
        directory.registerOrdererAdminTuple(row['User'], row['Orderer'], row['Organization'])

@given(u'user requests role for peer by creating a key and csr for peer and acquires signed certificate from organization')
def step_impl(context):
    assert 'table' in context, "Expected table with triplet of User/Peer/Organization"
    directory = bootstrap_util.getDirectory(context)
    for row in context.table.rows:
        directory.registerOrdererAdminTuple(row['User'], row['Peer'], row['Organization'])

@given(u'the peer network has organizations')
def step_impl(context):
    assert 'table' in context, "Expected table of peer network organizations"
    directory = bootstrap_util.getDirectory(context)
    for row in context.table.rows:
        org = directory.getOrganization(row['Organization'], shouldCreate = True)
        org.addToNetwork(bootstrap_util.Network.Peer)

@given(u'a ordererBootstrapAdmin is identified and given access to all public certificates and orderer node info')
def step_impl(context):
    directory = bootstrap_util.getDirectory(context)
    assert len(directory.ordererAdminTuples) > 0, "No orderer admin tuples defined!!!"
    # Simply create the user
    bootstrap_util.getOrdererBootstrapAdmin(context, shouldCreate=True)

@given(u'the ordererBootstrapAdmin creates the genesis block for chain "{ordererSystemChainId}" for network config policy "{networkConfigPolicy}" and consensus "{consensusType}" using chain creators policy "{chainCreatorPolicyNames}"')
def step_impl(context, ordererSystemChainId, networkConfigPolicy, consensusType, chainCreatorPolicyNames):
    ordererBootstrapAdmin = bootstrap_util.getOrdererBootstrapAdmin(context)
    # Retrieve the chainCreators config items required for now (tuple).
    chainCreatorsSignedConfigItems = ordererBootstrapAdmin.tags[chainCreatorPolicyNames]
    ordererSystemChainIdGUUID = ordererBootstrapAdmin.tags[ordererSystemChainId]

    (genesisBlock,envelope) = bootstrap_util.createGenesisBlock(context, ordererSystemChainIdGUUID, consensusType, signedConfigItems=list(chainCreatorsSignedConfigItems))
    bootstrap_util.OrdererGensisBlockCompositionCallback(context, genesisBlock)
    bootstrap_util.PeerCompositionCallback(context)

@given(u'the orderer admins inspect and approve the genesis block for chain "{chainId}"')
def step_impl(context, chainId):
    pass

@given(u'the orderer admins use the genesis block for chain "{chainId}" to configure orderers')
def step_impl(context, chainId):
    pass
    #raise NotImplementedError(u'STEP: Given the orderer admins use the genesis block for chain "test_chainid" to configure orderers')

@given(u'the ordererBootstrapAdmin generates a GUUID to identify the orderer system chain and refer to it by name as "{ordererSystemChainId}"')
def step_impl(context, ordererSystemChainId):
    directory = bootstrap_util.getDirectory(context)
    ordererBootstrapAdmin = bootstrap_util.getOrdererBootstrapAdmin(context)
    ordererBootstrapAdmin.tags[ordererSystemChainId] = bootstrap_util.GetUUID()


@given(u'the ordererBootstrapAdmin creates a chain creators policy "{chainCreatePolicyName}" (network name) for peer orgs who wish to form a network using orderer system chain "{ordererSystemChainId}"')
def step_impl(context, chainCreatePolicyName, ordererSystemChainId):
    directory = bootstrap_util.getDirectory(context)
    ordererBootstrapAdmin = bootstrap_util.getOrdererBootstrapAdmin(context)
    ordererSystemChainIdGuuid = ordererBootstrapAdmin.tags[ordererSystemChainId]

    # Collect the orgs from the table
    orgNames = [row['Organization'] for row in context.table.rows]

    (chainCreationPolicyNamesSignedConfigItem, chainCreatorsOrgsPolicySignedConfigItem) = \
        bootstrap_util.createChainCreatorsPolicy(context=context, chainCreatePolicyName=chainCreatePolicyName, chaindId=ordererSystemChainIdGuuid, orgNames=orgNames)

    ordererBootstrapAdmin.tags[chainCreatePolicyName] = (chainCreationPolicyNamesSignedConfigItem, chainCreatorsOrgsPolicySignedConfigItem)


@given(u'the ordererBootstrapAdmin runs the channel template tool to create the orderer configuration template "{templateName}" for application developers using orderer "{ordererComposeService}"')
def step_impl(context, templateName, ordererComposeService):
    pass


@given(u'the ordererBootstrapAdmin distributes orderer configuration template "template1" and chain creation policy name "chainCreatePolicy1"')
def step_impl(context):
    pass


@given(u'the user "{userName}" creates a peer template "{templateName}" with chaincode deployment policy using chain creation policy name "{chainCreatePolicyName}" and peer organizations')
def step_impl(context, userName, templateName, chainCreatePolicyName):
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName)
    pass

@given(u'the user "{userName}" creates a signedConfigEnvelope "{createChannelSignedConfigEnvelope}"')
def step_impl(context, userName, createChannelSignedConfigEnvelope):
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName)
    ordererBootstrapAdmin = bootstrap_util.getOrdererBootstrapAdmin(context)

    muralisRequiredSignedConfigItems = []

    channelID = context.table.rows[0]["ChannelID"]
    chainCreationPolicyName = context.table.rows[0]["Chain Creation Policy Name"]

    # Intermediate step until template tool is ready
    signedConfigItems = bootstrap_util.createSignedConfigItems(context, channelID, "solo", signedConfigItems=muralisRequiredSignedConfigItems)

    #NOTE: Conidered passing signing key for appDeveloper, but decided that the peer org signatures they need to collect subsequently should be proper way
    signedConfigEnvelope = bootstrap_util.signInitialChainConfig(signedConfigItems=signedConfigItems, chainId=channelID, chainCreationPolicyName=chainCreationPolicyName)

    user.tags[createChannelSignedConfigEnvelope] =  ChannelCreationInfo(channelID, chainCreationPolicyName, signedConfigEnvelope)

    # Construct TX Config Envelope, broadcast, expect success, and then connect to deliver to revtrieve block.
    # Make sure the blockdata exactly the TxConfigEnvelope I submitted.
    # txConfigEnvelope = bootstrap_util.createConfigTxEnvelope(chainId=channelID, signedConfigEnvelope=signedConfigEnvelope)


@given(u'the following application developers are defined for peer organizations')
def step_impl(context):
    assert 'table' in context, "Expected table with triplet of Developer/ChainCreationPolicyName/Organization"
    directory = bootstrap_util.getDirectory(context)
    for row in context.table.rows:
        directory.registerOrdererAdminTuple(row['Developer'], row['ChainCreationPolicyName'], row['Organization'])

@given(u'the user "{userName}" collects signatures for signedConfigEnvelope "{createChannelSignedConfigEnvelopeName}" from peer orgs')
def step_impl(context, userName, createChannelSignedConfigEnvelopeName):
    assert 'table' in context, "Expected table of peer organizations"
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName=userName)
    # Get the ChannelCreationInfo object that holds the signedConfigEnvelope
    channelCreationInfo = user.tags[createChannelSignedConfigEnvelopeName]
    signedConfigEnvelope = channelCreationInfo.signedConfigEnvelope
    for row in context.table.rows:
        org = directory.getOrganization(row['Organization'])
        assert bootstrap_util.Network.Peer in org.networks, "Organization '{0}' not in Peer network".format(org.name)
        bootstrap_util.BootstrapHelper.addSignatureToSignedConfigItem(signedConfigEnvelope.Items[0], (org.ecdsaSigningKey, org.getSelfSignedCert()))
    print("Signatures for signedConfigEnvelope:\n {0}\n".format(signedConfigEnvelope.Items[0]))

@given(u'the user "{userName}" creates config Tx "{configTxName}" using signedConfigEnvelope "{createChannelSignedConfigEnvelopeName}"')
def step_impl(context, userName, configTxName, createChannelSignedConfigEnvelopeName):
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName=userName)
    channelCreationInfo = user.tags[createChannelSignedConfigEnvelopeName]
    user.tags[configTxName] = bootstrap_util.createConfigTxEnvelope(channelCreationInfo.channelId, channelCreationInfo.signedConfigEnvelope)

@given(u'the user "{userName}" broadcasts config Tx "{configTxName}" to orderer "{orderer}" to create channel "{channelId}"')
def step_impl(context, userName, configTxName, orderer, channelId):
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName=userName)
    configTxEnvelope = user.tags[configTxName]
    bootstrap_util.broadcastCreateChannelConfigTx(context=context, composeService=orderer, chainId=channelId, user=user, configTxEnvelope=configTxEnvelope)

@when(u'user "{userName}" connects to deliver function on orderer "{composeService}"')
def step_impl(context, userName, composeService):
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName=userName)
    user.connectToDeliverFunction(context, composeService)

@when(u'user "{userName}" sends deliver a seek request on orderer "{composeService}" with properties')
def step_impl(context, userName, composeService):
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName=userName)
    row = context.table.rows[0]
    chainID = row['ChainId']
    start, end, = orderer_util.convertSeek(row['Start']), orderer_util.convertSeek(row['End'])

    streamHelper = user.getDelivererStreamHelper(context, composeService)
    streamHelper.seekToRange(chainID=chainID, start = start, end = end)

@then(u'user "{userName}" should get a delivery "{deliveryName}" from "{composeService}" of "{expectedBlocks}" blocks with "{numMsgsToBroadcast}" messages within "{batchTimeout}" seconds')
def step_impl(context, userName, deliveryName, composeService, expectedBlocks, numMsgsToBroadcast, batchTimeout):
    directory = bootstrap_util.getDirectory(context)
    user = directory.getUser(userName=userName)
    streamHelper = user.getDelivererStreamHelper(context, composeService)

    blocks = streamHelper.getBlocks()

    # Verify block count
    assert len(blocks) == int(expectedBlocks), "Expected {0} blocks, received {1}".format(expectedBlocks, len(blocks))
