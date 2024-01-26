import numpy as np
import matplotlib.pyplot as plt

def calculate_distance(agent_i, agent_j):
    '''
        Calculate the distance between two agents
        
        Parameters:
            agent_i (list): The position of agent i
            agent_j (list): The position of agent j
        
        Returns:
            float: The distance between agent i and agent j
    '''
    return np.sqrt((agent_i[0] - agent_j[0])**2 + (agent_i[1] - agent_j[1])**2)


def calculate_aij(alpha, delta, rij, r0, v):
    '''
        Calculate the aij value
        
        Parameters:
            alpha (float): A system parameter about antenna characteristics
            delta (float): The required application data rate
            rij (float): The distance between two agents
            r0 (float): Reference distance value
            v (float): Path loss exponent
        
        Returns:
            float: The calculated aij (communication quality in antenna near-field) value
    '''
    return np.exp(-alpha*(2**delta-1)*(rij/r0)**v)


def calculate_gij(rij, r0):
    '''
        Calculate the gij value
        
        Parameters:
            rij (float): The distance between two agents
            r0 (float): Reference distance value
        
        Returns:
            float: The calculated gij (communication quality in antenna far-field) value
    '''
    return rij / np.sqrt(rij**2 + r0**2)


def calculate_rho_ij(beta, v, rij, r0):
    '''
        Calculate the rho_ij (the derivative of phi_ij) value
        
        Parameters:
            beta (float): alpha * (2**delta - 1)
            v (float): Path loss exponent
            rij (float): The distance between two agents
            r0 (float): Reference distance value
        
        Returns:
            float: The calculated rho_ij value
    '''
    return (-beta*v*rij**(v+2) - beta*v*(r0**2)*(rij**v) + r0**(v+2))*np.exp(-beta*(rij/r0)**v)/np.sqrt((rij**2 + r0**2)**3)


def calculate_Jn(communication_qualities, neighbor_agent, PT):
    '''
        Calculate the Jn (average communication performance indicator) value

        Parameters:
            communication_qualities (numpy.ndarray): The communication qualities matrix among agents
            neighbor_agent (numpy.ndarray): The neighbor_agent matrix which is adjacency matrix of aij value
            PT (float): The reception probability threshold
        
        Returns:
            float: The calculated Jn value
    '''
    total_communication_quality = 0
    total_neighbors = 0
    swarm_size = communication_qualities.shape[0]
    for i in range(swarm_size):
        for j in range(swarm_size):
            if neighbor_agent[i, j] > PT:
                total_communication_quality += communication_qualities[i, j]
                total_neighbors += 1
    return total_communication_quality / total_neighbors


def calculate_rn(distances, neighbor_agent, PT):
    '''
        Calculate the rn (average distance) value

        Parameters:
            distances (numpy.ndarray): The distances matrix among agents
            neighbor_agent (numpy.ndarray): The neighbor_agent matrix which is adjacency matrix of aij value
            PT (float): The reception probability threshold
        
        Returns:
            float: The calculated rn value
    '''
    total_distance = 0
    total_neighbors = 0
    swarm_size = distances.shape[0]
    for i in range(swarm_size):
        for j in range(swarm_size):
            if neighbor_agent[i, j] > PT:
                total_distance += distances[i, j]
                total_neighbors += 1
    return total_distance / total_neighbors

def plot_figures(axs, t_elapsed, Jn, rn, swarm_position, PT, communication_qualities, swarm_size, swarm_paths, node_colors, line_colors):
    '''
        Plot 4 figures (Formation Scene, Swarm Trajectories, Jn Performance, rn Performance)
        
        Parameters:
            axs (numpy.ndarray): The axes of the figure
            t_elapsed (list): The elapsed time
            Jn (list): The Jn values
            rn (list): The rn values
            swarm_position (numpy.ndarray): The positions of the swarm
            PT (float): The reception probability threshold
            communication_qualities (numpy.ndarray): The communication qualities matrix among agents
            swarm_size (int): The number of agents in the swarm
            swarm_paths (list): The paths of the swarm
            node_colors (list): The colors of the nodes
            line_colors (list): The colors of the lines
        
        Returns:
            None
    '''
    for ax in axs.flatten():
        ax.clear()

    ########################
    # Plot formation scene #
    ########################
    axs[0, 0].set_title('Formation Scene')
    axs[0, 0].set_xlabel('$x$')
    axs[0, 0].set_ylabel('$y$', rotation=0)

    # Plot the nodes
    for i in range(swarm_position.shape[0]):
        axs[0, 0].scatter(*swarm_position[i], color=node_colors[i])

    # Plot the edges
    for i in range(swarm_position.shape[0]):
        for j in range(i+1, swarm_position.shape[0]):
            if communication_qualities[i, j] > PT:
                axs[0, 0].plot(*zip(swarm_position[i], swarm_position[j]), color=line_colors[i, j], linestyle='--')

    ###########################
    # Plot swarm trajectories #
    ###########################
    axs[0, 1].set_title('Swarm Trajectories')
    axs[0, 1].set_xlabel('$x$')
    axs[0, 1].set_ylabel('$y$', rotation=0)

    # Store the current swarm positions
    swarm_paths.append(swarm_position.copy())

    # Convert the list of positions to a numpy array
    trajectory_array = np.array(swarm_paths)

    # Plot the trajectories
    for i in range(swarm_position.shape[0]):
        axs[0, 1].plot(trajectory_array[:, i, 0], trajectory_array[:, i, 1], color=node_colors[i])
        # Calculate the differences between consecutive points
        dx = np.diff(trajectory_array[::swarm_size, i, 0])
        dy = np.diff(trajectory_array[::swarm_size, i, 1])
        
        # Normalize the vectors
        dx_norm = dx / np.sqrt(dx**2 + dy**2)
        dy_norm = dy / np.sqrt(dx**2 + dy**2)

        # Scale the vectors by a constant factor
        scale_factor = 2
        dx_scaled = dx_norm * scale_factor
        dy_scaled = dy_norm * scale_factor

        # Plot the trajectory with larger arrows
        axs[0, 1].quiver(trajectory_array[::swarm_size, i, 0][:-1], trajectory_array[::swarm_size, i, 1][:-1], dx_scaled, dy_scaled, color=node_colors[i], scale_units='xy', angles='xy', scale=1, headlength=10, headaxislength=9, headwidth=8)
        
    # Plot the initial positions
    axs[0, 1].scatter(trajectory_array[0, :, 0], trajectory_array[0, :, 1], color=node_colors)

    #######################
    # Plot Jn performance #
    #######################
    axs[1, 0].set_title('Average Communication Performance Indicator')
    axs[1, 0].plot(t_elapsed, Jn)
    axs[1, 0].set_xlabel('$t(s)$')
    axs[1, 0].set_ylabel('$J_n$', rotation=0, labelpad=20)
    axs[1, 0].text(t_elapsed[-1], Jn[-1], 'Jn={:.4f}'.format(Jn[-1]), ha='right', va='top')

    #######################
    # Plot rn performance #
    #######################
    axs[1, 1].set_title('Average Distance Performance Indicator')
    axs[1, 1].plot(t_elapsed, rn)
    axs[1, 1].set_xlabel('$t(s)$')
    axs[1, 1].set_ylabel('$r_n$', rotation=0, labelpad=20)
    axs[1, 1].text(t_elapsed[-1], rn[-1], '$r_n$={:.4f}'.format(rn[-1]), ha='right', va='top')

    plt.tight_layout()
    plt.draw()
    plt.pause(0.01)