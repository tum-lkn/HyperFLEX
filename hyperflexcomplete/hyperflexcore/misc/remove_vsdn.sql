-- Removes all entries from the database related to a VSDN request
-- leaves the database with just the physical topology
USE HyperFlexTopologyDevelop;
truncate FlowVisorFlowMatch;
truncate FlowVisorFlowSpace;
truncate SlicePermission;
truncate LogicalEdge;
truncate LogicalEdgeEmbedding;
truncate SwitchToVsdn;
-- Use @pedge_ids to store ids of physical edges. Since we are in safe mode -
-- and I have no intention to change this - deletion must be performed using
-- primary key column.

-- This senseles SELECT * FROM is necessary because MYSQL does not allow referencing
-- of the same table in a subselect for mutating queries.
-- Using this notation the necessary fiels seem to be copied into a temporary
-- variable and then ist fine. Another example of epic fails in software.
-- But if you ask guys from MySQL its probably not a bug but a feature!
DELETE FROM PhysicalEdge WHERE id IN (
    SELECT id
    FROM (SELECT * FROM PhysicalEdge) as temp
    WHERE 
        node_one_id IN (
            SELECT network_node_id FROM Controller
        ) OR node_two_id IN (
            SELECT network_node_id FROM Controller
        )
);
UPDATE Hypervisor SET used_cpu=0, cfg_msg_rate=0 WHERE network_node_id IN (
    SELECT network_node_id FROM (SELECT * FROM Hypervisor) as tmp
);
DELETE FROM NetworkNode WHERE id IN (SELECT network_node_id FROM Controller);
truncate Controller;
truncate Vsdn;
